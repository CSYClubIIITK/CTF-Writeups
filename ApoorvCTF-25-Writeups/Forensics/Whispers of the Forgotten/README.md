## Description
Lost echoes of the past await those who can see beyond the surface, revealing secrets hidden in the void.

- Author: Suraj
- flag: apoorvctf{ur1s_n3v3r_1i3}

**Category : Forensics**

## Writeup
We've been provided with a `.mem` file. To determine what kind of file it is, we use the `file` command:  

```
file memdump.mem 
memdump.mem: Windows Event Trace Log
```


This identifies the file as a **Windows Event Trace Log**. Windows Event Tracing is a logging mechanism that captures system and application activity, which can be useful for diagnosing issues, monitoring security events, or performing forensic analysis.  

For further investigation, we use **Volatility**, an open-source memory forensics framework that allows us to analyze memory dumps without modifying the original data. It supports various plugins that help uncover important forensic artifacts such as running processes, network connections, and user activity.  

Before diving into specific artifacts, we need to determine the system profile using `imageinfo`. This helps us identify the OS version and the appropriate Volatility profile for further analysis.  

```
python2 vol.py -f memdump.mem imageinfo
Volatility Foundation Volatility Framework 2.6.1
INFO    : volatility.debug    : Determining profile based on KDBG search...
          Suggested Profile(s) : Win10x64_19041
                     AS Layer1 : SkipDuplicatesAMD64PagedMemory (Kernel AS)
                     AS Layer2 : FileAddressSpace (memdump.mem)
                      PAE type : No PAE
                           DTB : 0x1aa000L
                          KDBG : 0xf8035fa12b20L
          Number of Processors : 4
     Image Type (Service Pack) : 0
                KPCR for CPU 0 : 0xfffff8035e8ce000L
                KPCR for CPU 1 : 0xffffbf81ed9e0000L
                KPCR for CPU 2 : 0xffffbf81ed3e4000L
                KPCR for CPU 3 : 0xffffbf81ed762000L
             KUSER_SHARED_DATA : 0xfffff78000000000L
           Image date and time : 2025-02-06 16:30:39 UTC+0000
     Image local date and time : 2025-02-06 16:30:39 +0000

```


This command provides a list of possible OS profiles. This suggests that we need to use Win10x64_19041 as our profile

Once we have the correct profile, we list the processes that were active when the memory dump was taken:  

```
python2 vol.py -f memdump.mem --profile=Win10x64_19041 pslist
Volatility Foundation Volatility Framework 2.6.1
Offset(V)          Name                    PID   PPID   Thds     Hnds   Sess  Wow64 Start                          Exit                          
------------------ -------------------- ------ ------ ------ -------- ------ ------ ------------------------------ ------------------------------
0xffffd50f09e67040 System                    4      0    165        0 ------      0 2025-02-06 21:58:06 UTC+0000                                 
0xffffd50f09fcf040 Registry                108      4      4        0 ------      0 2025-02-06 21:58:00 UTC+0000                                 
0xffffd50f0a702080 smss.exe                376      4      2        0 ------      0 2025-02-06 21:58:06 UTC+0000                                 
0xffffd50f0a93e080 csrss.exe               492    472     11        0      0      0 2025-02-06 21:58:07 UTC+0000                                 
0xffffd50f0cf8f080 wininit.exe             568    472      1        0      0      0 2025-02-06 21:58:07 UTC+0000                                 
0xffffd50f0cfba140 csrss.exe               576    560     12        0      1      0 2025-02-06 21:58:07 UTC+0000                                 
.
.
.                                 
0xffffd50f10a282c0 svchost.exe            1376    712      4        0      0      0 2025-02-06 21:58:09 UTC+0000                                 
.
.                                
0xffffd50f1130e080 chrome.exe             3436   2356     44        0      1      0 2025-02-06 16:28:57 UTC+0000                                 
0xffffd50f10ed6080 chrome.exe             3572   3436      8        0      1      0 2025-02-06 16:28:57 UTC+0000                                 
0xffffd50f117af300 chrome.exe             2928   3436     19        0      1      0 2025-02-06 16:28:59 UTC+0000                                 
0xffffd50f1165c2c0 chrome.exe             4696   3436     20        0      1      0 2025-02-06 16:28:59 UTC+0000                                 
0xffffd50f106d70c0 chrome.exe             4808   3436      8        0      1      0 2025-02-06 16:29:00 UTC+0000                                 
0xffffd50f1220c080 chrome.exe             6636   3436      8        0      1      0 2025-02-06 16:29:09 UTC+0000                                 
0xffffd50f126ba080 chrome.exe             6644   3436     15        0      1      0 2025-02-06 16:29:09 UTC+0000                                 
0xffffd50f125ab080 dllhost.exe            7148    836     15        0      1      0 2025-02-06 16:29:45 UTC+0000                                 
0xffffd50f0c742080 FTK Imager.exe         6328   2356     25        0      1      0 2025-02-06 16:29:57 UTC+0000                                 
0xffffd50f1094b340 svchost.exe            6604    712     14        0      0      0 2025-02-06 16:30:14 UTC+0000                                 
0xffffd50f11c46080 sppsvc.exe             6832    712      9        0      0      0 2025-02-06 16:30:16 UTC+0000                                 
0xffffd50f11c4d080 svchost.exe            2864    712     15        0      0      0 2025-02-06 16:30:17 UTC+0000                                 

```

This helps us identify any suspicious or unusual processes that may indicate malware or unauthorized activity. Looking at the process list, we notice that `Chrome is running`, suggesting that the user was actively using the browser at the time the memory snapshot was taken.  


Since Chrome was in use, we can leverage the `chromehistory` plugin in Volatility to extract browsing activity stored in memory:

```
python2 vol.py -f memdump.mem --profile=Win10x64_19041 chromehistory
Volatility Foundation Volatility Framework 2.6.1
Index  URL                                                                              Title                                                                            Visits Typed Last Visit Time            Hidden Favicon ID
------ -------------------------------------------------------------------------------- -------------------------------------------------------------------------------- ------ ----- -------------------------- ------ ----------
     3 https://www.google.com/                                                          Google                                                                               14     0 2025-02-06 16:29:10.880236        N/A       
    21 https://thehackernews.com/                                                       The Hacker News | #1 Trusted Cybersecurity News Site                                  2     0 2025-02-06 12:09:26.717240        N/A       
     2 https://google.com/                                                              Google                                                                                7     7 2025-02-06 16:29:10.438357        N/A       
    27 https://workspace.google.com/intl/en-US/gmail/                                   Gmail: Private and secure email at no cost | Google Workspace                         2     0 2025-02-02 04:33:01.423161        N/A       
    26 https://accounts.google.com/ServiceLogi...ttps://mail.google.com/mail/u/0/&emr=1 Gmail: Private and secure email at no cost | Google Workspace                         2     0 2025-02-02 04:33:01.423161        N/A       
    .
    .
    .
       107 https://pastebin.com/zk0wH7Pj                                                    Junk - Pastebin.com                                                                   1     1 2025-02-04 17:00:41.665556        N/A       
   106 https://www.google.com/search?q=this+is...5IHBDcuMTGgB5HtAQ&sclient=gws-wiz-serp this is the flag YXBvb3J2Y3Rme2Y0a2VfRjFhZyEhIX0= - Google Search                     3     0 2025-02-04 16:59:50.592017        N/A       
   139 https://www.youtube.com/watch?v=g2fT-g9PX9o                                      Network Ports Explained - YouTube                                                     1     0 2025-02-06 16:23:32.390565        N/A       
    .
    .
    .
```

This retrieves details such as **visited URLs, page titles, access timestamps, and search queries**, which can help track user activity.
  

Among the extracted URLs, we notice a `Pastebin link` with the title `"Junk"` Visiting this Pastebin reveals the flag, completing our investigation.  

**Flag: `apoorvctf{ur1s_n3v3r_1i3}`**
