# Automated Portfolio Manager

## Project Overview

The Automated Portfolio Manager is a Python-based application that allows users to manage their investment portfolios efficiently. It includes features such as buying stocks in lots, setting target allocatons, and auitomatic rebalancing of the portfolio based on user-defined criteria. The application is designed to work with the Indonesian stock market, where stocks are traded in lots of 100 shares.

## Features

- **Portfolio Balance Management:** Add and view your portfolio balance in IDR.
- **Stock Purchases:** Buy stocks in lots (each lot equals 100 shares) directly from the app.
- **Set Target Allocations:** Define target allocations for each stock in your portfolio.
- **Automatic Rebalancing:** Automatically rebalance your portfolio based on the target allocations.
- **Data Persistence:** All portfolio data is stored in a SQLite database, ensuring that your data is saved between sessions.

## Tools and Technologies Used

- **Python:** The core programming language used to develop the application.
- **Streamlit:** A framework used to create the interactive web application.
- **SQLite:** A lightweight database used to store portfolio data.
- **yFinance:** A Python library used to fetch the latest stock prices.

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.8 or higher
- pip (Python package installer)
- Anaconda (optional but recommended for managing environments)

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/automated-portfolio-manager.git
   cd automated-portfolio-manager
