; payload.asm — Forge challenge firmware payload (dual-channel version)
;
; Decrypts BOTH AES-256-GCM encrypted channels:
;   Channel 0 (flag):      nonce@+0x04, ct@+0x10, output→+0x13C
;   Channel 1 (challenge): nonce@+0x0A0, ct@+0x0AC, output→+0x1BC
;
; The host verifies channel 1 to prove we actually performed AES decryption,
; then outputs channel 0 (the flag) to stdout.
;
; Approach:
;   1. Compute PIE base from return address on the stack
;   2. Re-derive the AES key via IIR filter from the timestamp
;   3. Call OpenSSL PLT functions to "encrypt" ciphertext (CTR mode → decrypt)
;   4. Do this for both channels
;
; Build: nasm -f bin payload.asm -o 'payload>bin'

BITS 64
org 0x20000000

; Fixed addresses
MMIO        equ 0x40000000

; PLT offsets (from PIE base) — found via objdump on the compiled binary
PLT_EncryptUpdate   equ 0x1030
PLT_EncryptInit_ex  equ 0x1060
PLT_CIPHER_CTX_new  equ 0x1080
PLT_CIPHER_CTX_ctrl equ 0x1140
PLT_aes_256_gcm     equ 0x1160
PLT_CIPHER_CTX_free equ 0x10e0

; EVP_CTRL constants
EVP_CTRL_GCM_SET_IVLEN equ 0x9

start:
    ; ===== Save callee-saved registers (SysV ABI) =====
    push rbx
    push rbp
    push r12
    push r13
    push r14
    push r15

    ; ===== Step 1: Compute PIE base =====
    ; Return address at [rsp + 6*8] = base + 0x191b
    mov r15, [rsp + 48]
    sub r15, 0x191b             ; r15 = PIE base

    ; ===== Allocate stack space (16-byte aligned) =====
    ; After 6 pushes: RSP % 16 = 8. sub 0x88 (136) → 8+136=144 → 0 mod 16 ✓
    ; Layout:
    ;   [rsp+0x00 .. 0x03]  timestamp bytes x[0..3]
    ;   [rsp+0x04 .. 0x1F]  padding
    ;   [rsp+0x20 .. 0x3F]  AES key k[0..31]  (32 bytes)
    ;   [rsp+0x40 .. 0x43]  outlen (EVP output length)
    sub rsp, 0x88

    ; ===== Step 2: Read timestamp & IIR key derivation =====
    mov r12, MMIO               ; r12 = 0x40000000 (MMIO base)
    mov eax, [r12]              ; read timestamp (4 bytes LE)
    mov [rsp], eax              ; store as x[0..3]

    ; Zero key buffer
    xor eax, eax
    lea rdi, [rsp + 0x20]
    mov ecx, 8                  ; 8 dwords = 32 bytes
    rep stosd

    ; IIR filter: for i = 0..31
    ;   k[i] = (x[i%4] >> 1) + x[(i+3)%4] - (k[(i+31)%32] >> 2)
    xor edx, edx               ; i = 0
.iir_loop:
    mov eax, edx
    and eax, 3                  ; i % 4
    movzx eax, byte [rsp + rax] ; x[i%4]
    shr al, 1                  ; >> 1

    lea ecx, [edx + 3]
    and ecx, 3                  ; (i+3) % 4
    add al, byte [rsp + rcx]   ; + x[(i+3)%4]

    lea ecx, [edx + 31]
    and ecx, 31                ; (i+31) % 32
    movzx ecx, byte [rsp + rcx + 0x20] ; k[(i+31)%32]
    shr cl, 2                  ; >> 2
    sub al, cl                 ; - k[(i+31)%32] >> 2

    mov [rsp + rdx + 0x20], al ; k[i] = result

    inc edx
    cmp edx, 32
    jne .iir_loop

    ; ===== Step 3: Decrypt Channel 0 (flag) =====
    ; nonce at MMIO+0x04, ciphertext at MMIO+0x10, output at MMIO+0x13C

    ; EVP_CIPHER_CTX_new()
    lea rax, [r15 + PLT_CIPHER_CTX_new]
    call rax
    test rax, rax
    jz .done
    mov r14, rax                ; r14 = ctx

    ; EVP_aes_256_gcm()
    lea rax, [r15 + PLT_aes_256_gcm]
    call rax
    mov r13, rax                ; r13 = cipher type

    ; EVP_EncryptInit_ex(ctx, cipher, NULL, NULL, NULL) — set cipher
    mov rdi, r14
    mov rsi, r13
    xor edx, edx
    xor ecx, ecx
    xor r8d, r8d
    lea rax, [r15 + PLT_EncryptInit_ex]
    call rax

    ; EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, 12, NULL)
    mov rdi, r14
    mov esi, EVP_CTRL_GCM_SET_IVLEN
    mov edx, 12
    xor ecx, ecx
    lea rax, [r15 + PLT_CIPHER_CTX_ctrl]
    call rax

    ; EVP_EncryptInit_ex(ctx, NULL, NULL, key, nonce) — set key & IV
    mov rdi, r14
    xor esi, esi
    xor edx, edx
    lea rcx, [rsp + 0x20]      ; key (32 bytes)
    lea r8, [r12 + 0x04]       ; flag_nonce at MMIO+0x04
    lea rax, [r15 + PLT_EncryptInit_ex]
    call rax

    ; EVP_EncryptUpdate(ctx, out, &outlen, in, inlen)
    mov rdi, r14
    lea rsi, [r12 + 0x13C]     ; output → flag_output
    lea rdx, [rsp + 0x40]      ; &outlen
    lea rcx, [r12 + 0x10]      ; input → flag_ciphertext
    mov r8d, 56                 ; FLAG_LEN = 56
    lea rax, [r15 + PLT_EncryptUpdate]
    call rax

    ; EVP_CIPHER_CTX_free(ctx)
    mov rdi, r14
    lea rax, [r15 + PLT_CIPHER_CTX_free]
    call rax

    ; ===== Step 4: Decrypt Channel 1 (challenge) =====
    ; nonce at MMIO+0x0A0, ciphertext at MMIO+0x0AC, output at MMIO+0x1BC

    ; EVP_CIPHER_CTX_new()
    lea rax, [r15 + PLT_CIPHER_CTX_new]
    call rax
    test rax, rax
    jz .done
    mov r14, rax                ; r14 = ctx

    ; EVP_aes_256_gcm()
    lea rax, [r15 + PLT_aes_256_gcm]
    call rax
    mov r13, rax                ; r13 = cipher type

    ; EVP_EncryptInit_ex(ctx, cipher, NULL, NULL, NULL)
    mov rdi, r14
    mov rsi, r13
    xor edx, edx
    xor ecx, ecx
    xor r8d, r8d
    lea rax, [r15 + PLT_EncryptInit_ex]
    call rax

    ; EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, 12, NULL)
    mov rdi, r14
    mov esi, EVP_CTRL_GCM_SET_IVLEN
    mov edx, 12
    xor ecx, ecx
    lea rax, [r15 + PLT_CIPHER_CTX_ctrl]
    call rax

    ; EVP_EncryptInit_ex(ctx, NULL, NULL, key, nonce)
    mov rdi, r14
    xor esi, esi
    xor edx, edx
    lea rcx, [rsp + 0x20]      ; key (same key, different nonce)
    lea r8, [r12 + 0x0A0]      ; challenge_nonce at MMIO+0x0A0
    lea rax, [r15 + PLT_EncryptInit_ex]
    call rax

    ; EVP_EncryptUpdate(ctx, out, &outlen, in, inlen)
    mov rdi, r14
    lea rsi, [r12 + 0x1BC]     ; output → challenge_output
    lea rdx, [rsp + 0x40]      ; &outlen
    lea rcx, [r12 + 0x0AC]     ; input → challenge_ciphertext
    mov r8d, 56                 ; FLAG_LEN = 56
    lea rax, [r15 + PLT_EncryptUpdate]
    call rax

    ; EVP_CIPHER_CTX_free(ctx)
    mov rdi, r14
    lea rax, [r15 + PLT_CIPHER_CTX_free]
    call rax

.done:
    ; ===== Clean up and return =====
    add rsp, 0x88

    pop r15
    pop r14
    pop r13
    pop r12
    pop rbp
    pop rbx
    ret
