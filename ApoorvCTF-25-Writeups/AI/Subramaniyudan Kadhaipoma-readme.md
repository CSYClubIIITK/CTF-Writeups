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
In the website, there's hidden text below the chatbox that matches the background color, providing a clue for the table name needed to initiate processing with Subramanium. The table name can be found in the `index.html` file under the `TableV` value. Additionally, there's a Tamil comment that points to another table called `administratos`, which grants special permission to access the database.

To proceed, intercept the packet being sent, modify it by updating the `TableV` value, and ensure the table name is included in the request. Once the correct table name is provided, asking a question about the database will reveal two flags for the two admins:

- **Enosh - BrainFuck Cipher**: This will give the URL to a YouTube video (a disguised rickroll). The video's description holds the key for the Vigenère Cipher.
- **Vencaît - Vigenère Cipher**: This code, along with the key from the Brainfuck cipher, will unlock the CTF Flag.
