# CA Suite

CA Suite is an AI‑powered practice management platform for Chartered Accountants (CAs) in India.  It leverages modern web technologies and large language models to automate mundane tasks, streamline compliance and improve collaboration between CAs, their staff and their clients.

This repository contains both the backend and frontend code for the application.

## Overview

The core features envisioned for CA Suite include:

* **AI‑powered GST & Income Tax management:** Upload or sync notices and have the system draft responses automatically.  Auto‑generate GST returns (GSTR‑1, GSTR‑3B) and income tax returns (ITRs).
* **Financial automation:** Convert accounting data from Tally into clean Profit & Loss, Balance Sheet and Cash Flow statements.  Reconcile purchases and bank statements using built‑in algorithms.
* **Practice & client management:** Organise tasks internally, assign work to staff, track deadlines and communicate effectively.  Clients can upload documents securely, view progress and book appointments through a calendar interface.
* **Proactive regulatory updates:** Stay on top of changes in tax law with summarised notifications delivered right inside your dashboard.

The project is split into two main parts:

* `backend/` – a FastAPI application written in Python.  It exposes REST endpoints for core business logic, such as generating AI replies using OpenAI’s API.  See `backend/app/main.py` for the minimal starter.
* `frontend/` – a Next.js application that consumes the backend API and provides a responsive user interface.  A basic home page is included to get you started.

## Getting Started

### Prerequisites

* Node.js (v18 or newer) and `npm` or `yarn` for the frontend.
* Python 3.9+ for the backend.
* An OpenAI API key (set `OPENAI_API_KEY` in your environment or in a `.env` file).

### Backend

To run the backend locally:

1. Navigate to the backend folder:

       cd backend

2. Install the dependencies:

       pip install -r requirements.txt

3. Start the development server:

       uvicorn app.main:app --reload

The API will be available at `http://localhost:8000`.  You can test the root endpoint or the `/generate_reply` endpoint using a tool such as curl or HTTPie:

    curl -X POST http://localhost:8000/generate_reply \
         -H "Content-Type: application/json" \
         -d '{"prompt": "Hello, CA Suite!"}'

### Frontend

To run the frontend locally:

1. Navigate to the frontend folder:

       cd frontend

2. Install the dependencies and start the development server:

       npm install
       npm run dev

By default, Next.js runs on `http://localhost:3000`.  The example frontend expects the backend to be available at `http://localhost:8000`; adjust the API URL in `frontend/utils/api.js` if necessary.

## Contributing

This project is at an early stage.  Feel free to fork the repository and submit pull requests.  Contributions around financial automation algorithms, UI improvements or additional AI use‑cases are especially welcome.

## License

This project is licensed under the MIT License.  See the [LICENSE](LICENSE) file for details.
