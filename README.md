
# Product/Market Fit Score Generator for Companies Using Salesforce CRM:
A Python implementation using opensource LLM model Llama3.1 (8B) with Ollama + Wikipedia APIs & Page URLs to fetch relevant publically available company information.


## Installation

- Create a Virtual Environment: To keep dependencies isolated, it's best to use a virtual environment. You can create one with the following command: 
```bash
  python -m venv .venv
```
- Activate the Virtual Environment:

- On Windows:
```bash
  .venv\Scripts\activate
```
- On Windows Using Git Bash:
```bash
  source .venv/Scripts/activate
```
- On macOS/Linux:
```bash
  source .venv/bin/activate
```
- Install Dependencies: Once the virtual environment is active, install the required packages:
```bash
  pip install -r requirements.txt
```




## Usage/Examples
- How to run?
```bash
  python demo.py <company_name>
```
- Example
```bash
  python demo.py Airtel
```



## Prerequisites 

- Python setup -> https://www.python.org/downloads/release/python-31110
- Ollama setup -> https://ollama.com
- Llama3.1 model setup -> https://ollama.com/library/llama3.1
- Confirm Ollama is running on http://localhost:11434

## Solution Approach and Rationale

Given that I had no prior experience in this domain, my initial challenge was to identify **open-source** or **free solutions** capable of providing comprehensive **company-related information**, such as **company name**, **employee size**, and **revenue**. After two days of research, I discovered two potential solutions: **Clearbit** and **Crunchbase**. Both of these services are **paid**, with Clearbit being the more straightforward option. However, I encountered difficulties obtaining the necessary **API key** for Clearbit.

Crunchbase, while providing extensive information, did not offer an **API** that met my primary requirement of searching by **company name** as a simple string. My goal was to leverage **open-source** or **free APIs** along with available **open-source AI models**.

To address this, I developed a **custom solution**. During my research, I came across a **Wikipedia API** that allowed me to fetch **company-related pages**. This API appeared suitable for retrieving the necessary data. I then focused on extracting relevant information from the Wikipedia page. Initially, I intended to use a locally hosted **LLM (Llama3.1)** to analyze the entire **HTML response**. However, I soon realized that my LLM could not handle the extensive **token size**.

I re-evaluated the Wikipedia page and identified a **```<table>```** element with a specific class that consistently contained the relevant information. By parsing this table, I was able to significantly reduce the **token size** and successfully process the data with my LLM.

The next challenge was to configure the LLM to provide responses exclusively in **JSON format**. I implemented this configuration and developed a **JSON parser** to handle the LLM's string output.

Finally, I devised a **scoring algorithm** for evaluating **product/market fit**. To ensure accuracy, I conducted additional research and consulted **ChatGPT** for industry-standard weights, given the difficulty in obtaining this data directly from the internet. The weights are adjustable within the code to accommodate future changes. This iterative approach led to the development of the final solution.

## Known Limitations
- **Inaccurate Revenue Interpretation**: As the solution relies on a locally hosted LLM to read and interpret data from HTML, there are occasional inaccuracies in interpreting revenue values. This can lead to less accurate scoring results. The LLM may misinterpret or incorrectly extract revenue information, impacting the overall accuracy of the product/market fit score.

- **Public Company Data Restriction**: The solution is designed to work specifically with public companies. It relies on the presence of a <table> with specific classes on the Wikipedia page to extract relevant information. If this table is not available on the page, or if the company is not publicly listed, the solution will not be able to proceed or provide a valid score.