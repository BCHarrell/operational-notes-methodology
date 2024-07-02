# Op Findings
*Recommended use: Insert a "Finding" placeholder through the command pallet, add the necessary details/images, and then link to the heading in the respective host's note. Images can be put inside of Admonition blocks to keep this tidy*

e.g.:
```` 
## SQL Injection (ExampleApp)
Details:
Blah blah blah

Images:
```ad-example
[[example-image.png]]
```

Host Note
[[DemoOp-Findings#SQL Injection (ExampleApp)]]
````

## SQL Injection (client.com login)
Details:
`' or 1=1;--` leads to auth bypass

Images:
```ad-example
collapse: yes
title: images
![[sql-injection-client-com.png]]
```
