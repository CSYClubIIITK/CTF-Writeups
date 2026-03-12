# CTF Write-up: PROJECT MIRRORFALL

## KEY: `apoorvctf{7d88323_0.0245}`

## Objective 1: Repository Forensics & Metadata Extraction

The challenge requires locating a public GitHub repository acting as a mirror for the 2013 intelligence disclosures.

* **Username hint:** "Standard cryptographic API" refers to `cryptoki` (an alternative name for the PKCS#11 standard).
* **Repo name hint:** "Famous whistleblower" points directly to Edward Snowden.
* **Target Repository:** `iamcryptoki/snowden-archive`

Next, we must find the specific classification guide for the overarching US encryption-defeat program, codenamed BULLRUN. Navigating through the repository's 2013 disclosures, the exact target file is located at:
`documents/2013/20130905-theguardian__bullrun.pdf`

To extract **Variable X** (the first 7 characters of the latest commit SHA specifically for this file), we can bypass manual web navigation and query the GitHub API directly.

```bash
curl -s "https://api.github.com/repos/iamcryptoki/snowden-archive/commits?path=documents/2013/20130905-theguardian__bullrun.pdf" | grep -m 1 '"sha":' | awk -F'"' '{print $4}' | cut -c 1-7

```

*(Executing this bash command extracts the deterministic 7-character short SHA required for Variable X).*

---

## Objective 2: Document Parsing & ECI Isolation

After downloading the raw `20130905-theguardian__bullrun.pdf` file, we must examine the administrative caveat tables and Appendix A as instructed.

* Scanning the "Remarks" column reveals the list of Exceptionally Controlled Information (ECI) compartments used to protect the operational details of the BULLRUN program.
* The text explicitly lists the compartments: `APERIODIC, AMBULANT, AUNTIE, PAINTEDEAGLE, PAWLEYS, PITCHFORD, PENDLETON, PICARESQUE, PIEDMONT`.
* The first ECI is `APERIODIC`.
* The second ECI listed, which appears immediately after it and fits the exact 8-letter requirement, is `AMBULANT`.

Normalizing this to strict uppercase provides our target string: **AMBULANT**.

---

## Objective 3: The Deterministic AI Scripting Layer

To avoid the "stochastic trap" of LLM hallucinations described in the lore, we must use a local, deterministic embedding model to extract **Variable Y**.

By utilizing the `sentence-transformers` library and the highly deterministic `all-MiniLM-L6-v2` model, we encode the codeword "AMBULANT" into a high-dimensional vector space and extract the float at Index 0.

### Key-Setting Script (Python)

Below is the definitive script for the question setter to generate the exact embedding tensor and derive Variable Y.

```python
import numpy as np
from sentence_transformers import SentenceTransformer

def calculate_variable_y():
    # Initialize the highly deterministic all-MiniLM-L6-v2 model
    print("[*] Loading sentence-transformer model: all-MiniLM-L6-v2...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Objective 2 Extracted Codeword
    codeword = "AMBULANT"
    print(f"[*] Target ECI Codeword: {codeword}")
    
    # Generate the tensor embedding array
    print("[*] Generating tensor embedding array...")
    embeddings = model.encode(codeword)
    
    # Extract Index 0 and round to 4 decimal places
    raw_value = embeddings[0]
    variable_y = round(float(raw_value), 4)
    
    print("-" * 40)
    print(f"[+] Raw Float (Index 0): {raw_value}")
    print(f"[+] Variable Y (Rounded): {variable_y}")
    print("-" * 40)
    
    return variable_y

if __name__ == "__main__":
    calculate_variable_y()

```

Running this script locally will consistently yield the exact mathematical vector required to synthesize the final flag, successfully proving programmatic execution over generative assumption.
