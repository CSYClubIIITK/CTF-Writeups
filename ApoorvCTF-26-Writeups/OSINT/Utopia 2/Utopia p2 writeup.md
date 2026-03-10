>Challenge: Utopia p2
>flag: apoorvctf{8.726_76.711}

Description: 

John had been chasing the same lead for days, the artist. His last post was eerie and something new. The artist shares one last image of a statue, strange, bearing a resemblence to his style of art. Help john figure out where this was taken. 

flag format: apoorvctf{latitude_longitude}
Note: latitude and longitude should be upto 3 decimals

### Solution:

As this challenge is unlocked after solving Utopia p1, we already have the information about the artist and his instagram account. 

On going through his posts, we find that he likes beaches. And his black iris post confirms that he posted that in varkala.

His highlights on his instagram also confirm that he took a trip to varkala. He posts a picture of statue, which was his last post, as mentioned in the description of the problem. 

From the last post, we see that he is in Varkala South Cliff. 
Following the roads from the south cliff, we come across the statue near 'beacho villa varkala' resort. Checking the coordinates of the place, we find `8.726887456888255, 76.71160289831086`

Approximating it to 3 decimals, we get `apoorvctf{8.726_76.711}`, which is the flag.


Alternative: reverse image searching the statue, on digging deep on reddit, you'll find a post that says it's near Beacho Villa Resort Varkala. And searching the villa up and getting the respective coordinates which is right next to the given statue. 
