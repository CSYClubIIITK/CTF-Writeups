const express = require('express');
const { createSigner, createVerifier } = require('fast-jwt')
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');
const app = express();
const port = 3000;

const publicKeyPath = path.join(__dirname, 'public_key.pem');
const publicKey = fs.readFileSync(publicKeyPath, 'utf8');
const privateKeyPath = path.join(__dirname, 'key');
const privateKey = fs.readFileSync(privateKeyPath, 'utf8');
const FLAG = "apoorvctf{qWe_jwt_qWe}";
app.use(bodyParser.json());
app.set('view engine', 'ejs');
app.use(bodyParser.json());
app.use(express.static('public'));
app.get('/', (req, res) => {
    res.render('index', { title: "Tanjiro is in big Trouble!", message: "Bruh, Tanjiro messed up BIG TIME. 😭 He hid Goku’s summoning scroll somewhere on this cursed website, and now it’s all broken. 💀 If we don’t find it fast, Goku’s never showing up, and we’re all doomed. No cap, this might be the hardest quest yet. Think you got what it takes? 👀🔥" });
});

app.get('/login', (req, res) => {
    const payload = { admin: false, name: req.query.name || "Guest" };
    const signSync = createSigner({ algorithm: 'RS256', key: privateKey });
    const token = signSync(payload);
    
    res.render('login', { title: "Login", token, message: "Use this token to explore!" });
});

function verifyToken(req, res, next) {
    const token = req.query.token;
    if (!token) return res.render('error', { title: "Error", message: "Tanjiro says you need a token to continue!" });
    try {
        const verifySync = createVerifier({ key: publicKey });
        const payload = verifySync(token);
        req.decoded = payload;
    } catch (err) {
        return res.render('error', { title: "Error", message: "I ain't reading all that." });
    }
    next();
}

app.get('/public', (req, res) => {
    res.render('public', { title: "Public Key", message : "Tanjiro left this key for us. It might be useful!", publicKey });
});

app.get('/admin', verifyToken, (req, res) => {
    res.render('admin', { 
        title: "The Forbidden Chamber 🔥", 
        decoded: req.decoded, 
        flag: FLAG, 
        message: "Welp... Goku ain’t pulling up. 😭 But he did leave you a lil’ something. 👀✨" 
    });
    });

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
