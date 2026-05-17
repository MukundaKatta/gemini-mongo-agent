# Atlas setup for the demo

A one-time click-through to wire MongoDB Atlas to this agent. Takes about five minutes.

1. Go to https://cloud.mongodb.com and sign in (or sign up, free).
2. Create a new Project, then click **Build a Database**.
3. Pick **M0 Free**. Choose any region. Click **Create Deployment**.
4. **Database Access** tab > **Add New Database User** > username + password (Built-in role: `readAnyDatabase`). Save the password.
5. **Network Access** tab > **Add IP Address** > **Allow Access From Anywhere** (`0.0.0.0/0`). Confirm.
   - Demo-only. Not production. Lock this down to your Cloud Run egress IPs before any real workload.
6. **Database** tab > your cluster > **Browse Collections** > **Load Sample Dataset**. Wait for it to finish (about 2 minutes).
7. Back on the **Database** tab, click **Connect** on the cluster > **Drivers** > **Python**.
8. Copy the SRV string. It looks like `mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority`.
9. Replace `<password>` with the real password (URL-encode special chars).
10. Export it locally:
    ```bash
    export MDB_MCP_CONNECTION_STRING='mongodb+srv://...'
    ```
11. Sanity-check with `npx mongodb-mcp-server@latest --readOnly`. It should connect and list tools.

Sample dataset used: `sample_mflix.movies` (and `embedded_movies` if you want vector search).
