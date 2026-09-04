# broseidon: When fast meets slower
*This file also includes FAQs (frequently asked to myself)*

**NOTE:** Work in Progress, and its denoted in the features table

## Extended description of capabilities:
Broseidon is created to manage my homelab. It could perform tasks on the simple scale like an online storage server, a calender, etc. I plan on also making it self-sustaining using AI, and using it as a planner. Normal planners just dont feel level with me so I default back to using AI, so lets turn it into a project.

## Machine specifications:

| Property         | Component              | Note                                                  |
| ---------------- | ---------------------- | ----------------------------------------------------- |
| Server Model     | Inspiron 3647          | The man himself                                       |
| Operating System | Fedora Server          | Balance performance and stability                     |
| CPU              | Intel i5 4460S         | Well it atleast says Super                            |
| GPU              | Intel HD Graphics 4600 | A rudimentary implant                                 |
| RAM              | 16GB DDR3              | Upgraded                                              |
| Storage          | 128gb SSD + 1TB HDD    | Upgraded, all SATA                                    |
| Network          | Ethernet               | Could be 1 gigabit but guess we'll never know         |
| Torment          | Since 2014             | Speechless (speechless)                               |
| Implants         | N/A                    | DVD swap, CMOS swap (larp), aiming for SATA expansion |
| Power Usage      | <220W                  | I aim to minimize this quantity                       |

## The name:
My best friend gave me this nickname, its so cool its now time to etch it into history.

## Why?:
This is a personal project and also open source. It is meant to serve as a display of skill. The next category about the technologies and ideas used will show what aspects and corners I cover. Look towards this as inspiration to start your journey.

## Technologies and Features:
*This category is to show on the global scope about what this project focuses on, look at ME employers!!!1!1*
*And just to include, performance and stability are measured relatively with my daily driver*

| Number | Feature                  | Usage                      | Performance | Stability | Implementation              | Module    | Present? | Extra Note                                                                         |
| ------ | ------------------------ | -------------------------- | ----------- | --------- | --------------------------- | --------- | -------- | ---------------------------------------------------------------------------------- |
| 1      | Linux OS                 | Server                     | 90%         | 90%       | Fedora                      | -         | F        | Over debian, for podman benefits                                                   |
| 2      | Mandatory Access Control | Security                   | 100%        | 99%       | SELinux                     | Package   | F        | For understanding enforcements (extra)                                             |
| 3      | Remote Access            | Remote Access              |             |           | Cockpit                     | Package   | F        | Great UI, complements SELinux and has a terminal                                   |
| 4      | File Storage             | File Storage               |             |           | FileBrowser                 | Package   | F        | Selectively fetch files from folders isntead of global scale browsing with Cockpit |
| 5      | Password Manager         | Storing passwords          |             |           | VaultWarden                 | Package   | F        | You may question uptime, obviously this is just a backup                           |
| 6      | Vector DB                | Storing embeddings         |             |           | Qdrant                      | qdrant    | F        | You live life once, start turning words into numbers                               |
| 7      | Embedding                | Convert text to embeddings |             |           | LLama.cpp and a .gguf model | llama.cpp | F        | CPU Build                                                                          |
| 8      | Calender                 |                            |             |           |                             |           |          | Probably one package to create/edit, and other to sync to an other online provider |
| 9      | Containerization         | Manage multiple pods       |             |           | podman                      | Package   | F        | For managing everything properly, and cockpit has support                          |
| 10     |                          |                            |             |           |                             |           |          |                                                                                    |
| 11     |                          |                            |             |           |                             |           |          |                                                                                    |
| 12     |                          |                            |             |           |                             |           |          |                                                                                    |
| 13     |                          |                            |             |           |                             |           |          |                                                                                    |
| 14     |                          |                            |             |           |                             |           |          |                                                                                    |
| 15     |                          |                            |             |           |                             |           |          |                                                                                    |
| 16     |                          |                            |             |           |                             |           |          |                                                                                    |
| 17     |                          |                            |             |           |                             |           |          |                                                                                    |
| 18     |                          |                            |             |           |                             |           |          |                                                                                    |
| 19     |                          |                            |             |           |                             |           |          |                                                                                    |
| 20     |                          |                            |             |           |                             |           |          |                                                                                    |
| 21     |                          |                            |             |           |                             |           |          |                                                                                    |


## Would this be applicable for YOUR workflow?:
This is an open source personal project made for myself. There is a 99.99% chance that this code will be os-dependant, and further, hardware-dependent. You can observe and learn implementations from this code, and if you want to implement an idea from here, do give credit for what its worth. The implications of the license imposed on this project allows you to do so. Notes would be added alongside functions to best explain what it does.

## Will this ever become a service?:
NO.
Long answer, the previous category mentions about how its very incapable of being universal. It is not made to do so. Turning this into a service is not planned.

## This is not industry standard:
Obviously, because this server only has integrated graphics, I cannot run GPU specific workloads, hence, I must resort to using CPU fallbacks of the workloads. The objective is learning not keeping. After years, I realized that the best server wont walk up to me, so now I've stepped forward myself to make the best out of what server I have.

## AI Usage policy:
Through my first ever proper hackathon, one must understand that genuinely 99% of the others did not know either. My principle is using AI for initialization, for stepping into a field I dont know. Accompanying that follows manual testing, and resolving incompatibilities done by me.

# Privacy standpoint:
Privacy is an expensive hobby. You might have thought that me hosting a password manager on a local server is for privacy, which I then spoil by allowing cloud AIs to access my files freely. I have realized that its better to go forward step-by-step with practices instead of spending years compiling the best one. One less company knows what I do, I rest tonight.

## Who is Interamps?:
My alternate account which I use for holding any code I wish to hold for the long term. A separate account to containerize my work (which sounds like larp). However all contributions are performed from my main account. I work in cybersecurity so I could also mention that I have limited my authority on myself so I do not hold extra permissions like deleting this repository on my main account.