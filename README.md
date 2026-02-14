# Student Performance Analysis 📊

An AI-powered tool to analyze student performance data, providing actionable insights and personalized mentorship.

## 🌟 Features

- **Data Ingestion**: Easily upload and parse student performance data (CSV).
- **Interactive Analytics**: Visualizations and statistical analysis of student grades and attendance.
- **AI Mentor**: A built-in AI mentor (powered by Gemini) that answers questions and provides guidance based on the data.
- **Automated Insights**: Automatically generates insights about trends, outliers, and areas for improvement.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/harishreddykottala-glitch/student-performance-analysis.git
    cd student-performance-analysis
    ```

2.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    - Create a `.env` file in the root directory.
    - Add your API keys (e.g., `GEMINI_API_KEY`) if required.

### Running the Application

1.  Start the application:
    ```bash
    python main.py
    ```

2.  Open your browser and navigate to `http://localhost:8000` (or the port specified in the console).

## 📁 Project Structure

- `main.py`: The entry point of the application.
- `services/`: Contains core logic for analytics, AI mentorship, and data ingestion.
- `static/`: Frontend assets (HTML, CSS, JS).
- `data/`: Sample data and CSV templates.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.