# ⚖️ Law & Verdict Scraper

A user-friendly web scraper built with Streamlit and Selenium to automatically download court judgments from the Rajasthan High Court website. It provides a simple interface to fetch judgments, saving them as individual PDFs and a summary CSV file.

---
## ✨ Functionalities

* **User-Friendly Web UI**: Built with **Streamlit** to provide a simple and interactive web interface, removing the need for complex command-line interaction.
* **Automated Scraping**: Uses **Selenium** to automate a real web browser, handling form submissions, CAPTCHA input, and navigating through multiple pages of results.
* **Incremental Downloads**: The app smartly keeps track of previously downloaded judgments in a local SQLite database. This ensures that on future runs, it only scrapes and downloads new or updated records, saving time and resources.
* **Organized Output**: Automatically saves all downloaded judgment files into a `PDFs` folder and all summary reports into a `CSVs` folder for easy access and management.

---
## 🚀 Getting Started Locally

Follow these steps to set up and run the project on your local machine.

### **Prerequisites**

Before you begin, ensure you have the following installed:
* **Python 3.9+**: [Download Python](https://www.python.org/downloads/)
* **pip** (usually comes with Python)
* **Git**: [Download Git](https://git-scm.com/downloads/)
* **Google Chrome**: The scraper uses Selenium with Chrome, so you must have the browser installed.

### **Installation & Setup**

1.  **Clone the Repository**
    Open your terminal or command prompt and clone this repository.
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```
    *(Replace `your-username/your-repo-name` with your actual repository URL)*

2.  **Create a Virtual Environment**
    It's highly recommended to use a virtual environment to keep project dependencies isolated.
    
    * On macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    * On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install Dependencies**
    With your virtual environment active, install all the required Python libraries from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

### **Running the Application**

1.  **Launch the Streamlit App**
    Run the following command in your terminal from the project's root directory:
    ```bash
    streamlit run app.py
    ```

2.  **Access the Scraper**
    Your web browser should automatically open a new tab with the application. If it doesn't, navigate to:
    [**http://localhost:8501**](http://localhost:8501)

You can now use the web interface to start scraping judgments. The files will be saved locally in the `PDFs` and `CSVs` folders within your project directory.
