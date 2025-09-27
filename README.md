The purpose of this project is to keep paperless-ngx documents in sync with OpenWebUI for use as knowledge during chat sessions with your LLM. Nothing needs to use the Internet for this and it can all be local for privacy purposes.

Install:
- Have a fully working setup for OpenWebUI and paperless-ngx
- Mv the .env.example to .env, and enter the appropriate values
- docker compose build && docker compose up

How does it work?
- Hashes of each file are kept in the volume to make sure duplicates are not re-processed. 

# TODO
- Cleanup the md directory for security. Don't want those laying around.

Original author and article
- https://www.reddit.com/user/carlinhush/
- https://www.reddit.com/r/Paperlessngx/comments/1np5sr4/paperlessngx_paperlessai_openwebui_i_am_blown/