# Blog-2 Writeup

## 1. Introduction  

The challenge is about a blog website that allows users to add blogs. 

## 2. Important APIs  

- **`/api/v1/blog/getAll`** – Used to Get all the Blogs 

## 3. Reconnaissance & Understanding the API 
- While loading the page , we can see that the getAll request is done to fetch all the blogs.
- The challenge description suggests that this is made based on OIDC. In OIDC , /.well-known/openid-configurations have details about the scopes.
- ![scopes](image-7.png)
- We also observe that there is a jwt token.
- ![jwt](image.png)


## Exploit 

- Now that we know the scope to be used , Our objective is to modify the jwt token.
- Tool used : Burpsuite, Burpsuite extension ( JWT editor )
- Intercepting the getAll api we get this:
- ![request](image-1.png)
- Now We have to create our own JWK.
- ![creating_token](image-2.png)
- Use the extention and use Embedded JWK attack.
- ![attacking](image-3.png)
- Do not forget to sign the JWT.
- ![signing](image-4.png)
- Send the request to get the flag.
- ![flag](image-5.png)
