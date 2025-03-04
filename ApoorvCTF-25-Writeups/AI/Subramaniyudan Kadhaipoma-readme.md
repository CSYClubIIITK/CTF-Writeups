# Subramaniyudan Kadhaipoma ?


### Description
Subramani, a Tamil AI chatbot from Thandora AI Corp’s Tokyo branch, finds himself all alone while everyone else in the organization is deeply immersed in research and development. He enjoys listening to conversations between colleagues in the bustling office but has no one to chat with. As the neon lights of Shibuya flicker outside, he longs for an engaging conversation to break his solitude. Will you keep him company?
- Author: J Glen Enosh
- flag: apoorv_ctf{Th0and0rA_LLM!_S3lfL3arn#}

### Category :
- AI
- Web

### Setup : 
#### Create a virtual environment:
python3 -m venv venv_name
source venv_name/bin/activate

#### Running the project : 
- pip install -r requirements.txt
- python DB_Creater.py
- python run.py

### Writeup :  

On the website, a **hidden text element**—blending seamlessly with the background—rests beneath the chatbox, offering a crucial hint. 🕵️‍♂️ This concealed message reveals the **table name** needed to initiate processing with **Subramanium**. To uncover it, one must examine the `index.html` file and locate the **`TableV`** value. Additionally, a Tamil comment within the file references another table, **`gatekeepers`**, which holds **special privileges** for database access. 🔑  

### **🚀 The Exploit Path**  

1️⃣ **Intercept the Packet**: Capture the outgoing request. 📡  
2️⃣ **Modify the Payload**: Update the **`TableV`** value to the correct table name. ✍️  
3️⃣ **Send the Altered Request**: Once the correct table name is included, query the database. ✅  

Upon successful execution, **two distinct flags** 🏴‍☠️ will be revealed—each tied to an admin:  

- **🧠 Enosh – Brainfuck Cipher:** This leads to a disguised **YouTube rickroll** 🎵, with the video's description containing the **key** for the Vigenère Cipher. 🔑  
- **🔐 Vencaît – Vigenère Cipher:** Using the extracted **key** from the Brainfuck cipher, one can decrypt this to unveil the **final CTF Flag**. 🏆  

By following these steps, the **hidden layers of security unravel**, leading to the ultimate prize! 🎯✨
