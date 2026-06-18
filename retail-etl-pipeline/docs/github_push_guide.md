# How to Push This Project to GitHub

Follow these steps exactly to get `retail-etl-pipeline` live on your GitHub.

---

## Step 1 — Create the Repo on GitHub

1. Go to [https://github.com/new](https://github.com/new)
2. Set **Repository name** to: `retail-etl-pipeline`
3. Set **Description** to: `YTG Retail — Customer Orders ETL Pipeline (Data Engineering Capstone)`
4. Choose **Public** (so your lecturer/assessor can see it)
5. **Do NOT** tick "Add a README file" — you already have one
6. Click **Create repository**

---

## Step 2 — Set Up Git Locally

Open your terminal (Command Prompt or Git Bash on Windows) and navigate to your project folder:

```bash
cd path/to/retail-etl-pipeline
```

Initialise git and connect to your GitHub repo:

```bash
git init
git add .
git commit -m "Initial commit: YTG Retail ETL Pipeline capstone project"
git branch -M main
git remote add origin https://github.com/<your-username>/retail-etl-pipeline.git
git push -u origin main
```

Replace `<your-username>` with your actual GitHub username.

---

## Step 3 — Verify on GitHub

Go to `https://github.com/<your-username>/retail-etl-pipeline` and confirm:

- ✅ `README.md` renders on the homepage
- ✅ `data/` folder contains all three CSV files
- ✅ `etl_pipeline.py` is present
- ✅ `tests/` folder is present
- ✅ `docs/` folder contains `data_dictionary.md`
- ✅ `.gitignore` is present
- ✅ `requirements.txt` is present

---

## Future Updates

To push any new changes after the initial commit:

```bash
git add .
git commit -m "describe what you changed"
git push
```
