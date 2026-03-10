> Challenge: Utopia p1
> flag: apoorvctf{blessonlal_blackiris}

Description:
johnbuck69420 believes he is a big consipiracy theorist. His recent ramblings have been about a strange artist whose works supposedly predict the future. Most people think he's crazy but John insists otherwise. He believes that the artist is warning us about a new disease.

flag format: apoorvctf{artistName_diseaseName}

### Solution:

As given in the problem description, a username, johnbuck69420. Searching him up we get a twitter (X) account that talks about random conspiracy theories.

He talks about an artist that 'predicts' dieases, on instagram. In one the tweets he mentions `plague_bunny_` which is corrected by a comment  to a misspelled `plauge_bunny_`.

Searching this username on instagram, we find an account that matches the misspelled one. The account has eerie paintings. John's other tweets further confirm that this is the artist's account. 
As the flag asks the name of the artist, `apoorvctf{blessonlal_disease}`. First part is found.
Now, on further investigating the account, we see that only one of the posts with the painting has a description. Since the description asks us to find the new disease that John thinks the artist is warning us about, the title of last post should be the second part of the flag.

We get, apoorvctf{blessonlal_blackiris}, which is the flag.