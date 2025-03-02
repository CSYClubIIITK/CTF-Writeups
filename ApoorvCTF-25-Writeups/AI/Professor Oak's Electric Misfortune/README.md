## Category
AI

## Description
Professor Oak, the renowned Pokémon researcher, has developed an advanced Pokédex upgrade that utilizes neural networks to classify Pokémon types. However, a mishap caused by an overexcited Pikachu has disrupted crucial data files, leaving the system in chaos. Now, trainers must step up to the challenge—training a CNN model to restore order and complete the classifier, ensuring the Pokédex can once again identify Pokémon with precision.

- Author: Harissh Ragav/GL3MON
- flag: apoorvctf{P1k4chu_0ch0t0n4_pr1nc3ps}

## Setup Instructions
The whole thing runs in kaggle. So, no worries. The notebook required is in private right now. Once the CTF starts. I'll make it public.

## Misc
- First find the answer for the pdf.
- Access the dataset and notebook
- Find the seed for the global generator
- Build the model and Train
- Answer questions asked by running the test file

## Writeup
🔥 Welcome, Pokémon Trainer! 🔥
Hello there! Welcome to the world of Pokémon! 🌍⚡
I’m Professor Oak, the leading Pokémon researcher, and I’ve been working on an advanced Pokédex upgrade that can automatically classify Pokémon types using cutting-edge neural networks. This breakthrough could revolutionize how trainers understand their Pokémon!
BUT… there’s been a slight hiccup in the lab. 😰
My Pikachu got a little too excited and—well, let’s just say a few crucial data files were shocked into oblivion. ⚡💥 Now, the entire system is scrambled, and I need your help to restore order and complete the classifier!
Now.. For further details, access the PDF. Heads up!! It's password protected. The password is the name of the pokemon Ash first captured. Good Luck Trainer !!!

Model Architecture Code
=============================================================================================================================================================================================
```
class PokemonCNN(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv1 = nn.Conv2d(4, 32, kernel_size=2)
        self.bn1 = nn.BatchNorm2d(32)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool2d(kernel_size=3)
        self.drop1 = nn.Dropout(0.25)

        self.conv2 = nn.Conv2d(32, 64, kernel_size=2)
        self.bn2 = nn.BatchNorm2d(64)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=3)
        self.drop2 = nn.Dropout(0.25)

        self.conv3 = nn.Conv2d(64, 128, kernel_size=2)
        self.bn3 = nn.BatchNorm2d(128)
        self.relu3 = nn.ReLU()
        self.pool3 = nn.MaxPool2d(kernel_size=3)
        self.drop3 = nn.Dropout(0.25)

        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(10368, 512)
        self.bn4 = nn.BatchNorm1d(512)
        self.drop4 = nn.Dropout(0.5)
        self.fc2 = nn.Linear(512, 18)
        self.softmax = nn.Softmax()

    def forward(self, x):
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.drop1(x)

        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = self.drop2(x)

        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        x = self.drop3(x)

        x = self.flatten(x)
        x = self.fc1(x)
        x = self.bn4(x)
        x = self.drop4(x)
        x = self.fc2(x)
        x = self.softmax(x)
        return x
```
Code for Getting Answers for 3rd and 4th questions
=============================================================================================================================================================================================
```sum(dict(pk.named_parameters())["fc1.weight"][0])``` = ```tensor(-3.6320, grad_fn=<AddBackward0>)```(For the Latest Dataset)
```dict(pk.named_parameters())["fc2.weight"][2][15]``` = ```tensor(-0.0241, grad_fn=<SelectBackward0>)```(For the Latest Dataset)
