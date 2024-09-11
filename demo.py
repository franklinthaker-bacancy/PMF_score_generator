""" 
We need to get following exercise done by the candidate and share it along with the profile:

Exercise Overview: 
The candidate will build a scoring system to evaluate product/market fit for companies using Salesforce CRM, based on free AI models and publicly available data sources.

Requirements:
Input: Any Company name (i.e. Airtel or Maruti Suzuki).
Output: Product/market fit score for Salesforce CRM.
Tools: Any free framework, language, or AI model.
Deliverables: Functional code and clear documentation explaining the thought process.
This exercise should provide us with valuable insights into the candidate's ability to produce well-documented, high-quality deliverables. 
"""

import json
import logging
import re
import requests
import sys
import typing as t
from bs4 import BeautifulSoup

MODEL: str = "llama3.1"
OLLAMA_URL: str = "http://localhost:11434/api/generate"
DEFAULT_MAX_EMP_SIZE: int = 500000  # Maximum employee size for normalization
DEFAULT_MAX_REVENUE: float = (
    100000000000000  # Maximum revenue for normalization # 100T$
)
DEFAULT_WEIGHT_EMP_SIZE: float = 0.3
DEFAULT_WEIGHT_REVENUE: float = 0.7
DEFAULT_WEIGHT_INDUSTRY: float = 0.2
DEFAULT_WEIGHT_INDUSTRY_SCORE: float = 0.5

headers: t.Dict[str, str] = {
    "Content-Type": "application/json",
    "Accept": "*/*",
}

# Define weights for each factor (adjust as needed)
standard_industry_data: t.Dict[str, t.Any] = {
    "automotive": {
        "weight_emp_size": 0.4,
        "weight_revenue": 0.4,
        "weight_industry": 0.2,
        "industry_score": 0.85,
        "max_emp_size": 500000,
        "max_revenue": 500000000000,
    },
    "telecommunications": {
        "weight_emp_size": 0.3,
        "weight_revenue": 0.5,
        "weight_industry": 0.2,
        "industry_score": 0.9,
        "max_emp_size": 300000,
        "max_revenue": 300000000000,
    },
    "healthcare": {
        "weight_emp_size": 0.3,
        "weight_revenue": 0.5,
        "weight_industry": 0.2,
        "industry_score": 0.9,
        "max_emp_size": 1000000,
        "max_revenue": 400000000000,
    },
    "retail": {
        "weight_emp_size": 0.3,
        "weight_revenue": 0.4,
        "weight_industry": 0.3,
        "industry_score": 0.7,
        "max_emp_size": 2000000,
        "max_revenue": 600000000000,
    },
    "financial services": {
        "weight_emp_size": 0.25,
        "weight_revenue": 0.55,
        "weight_industry": 0.2,
        "industry_score": 0.8,
        "max_emp_size": 500000,
        "max_revenue": 500000000000,
    },
    "Audio streamingPodcasting": {
        "weight_emp_size": 0.2,
        "weight_revenue": 0.5,
        "weight_industry": 0.3,
        "industry_score": 0.65,
        "max_emp_size": 20000,
        "max_revenue": 10000000000,
    },
}

prompt: str = f"""
    Please extract company information from the following object and Convert revenue like '15B' to a number (e.g., 15000000000) always and respond only in the strict JSON format shown below:
    {{
      company_name:str = "",
      employee_size:int = 0,
      revenue:int = 0,
      industry:str = ""
    }}
"""


# Define normalization ranges
def normalize(value: int, max_value: int) -> float:
    return min(value / max_value, 1) if max_value else 0


def extract_json_from_response(response_text: str) -> t.Dict[str, t.Any]:
    # Use regex to find the JSON part within the response
    json_match: str = re.search(r"\{.*\}", response_text, re.DOTALL)

    if not json_match:
        raise json.JSONDecodeError("JSON not found in the response.")

    json_string: str = json_match.group(0)

    try:
        # Parse the JSON string into a Python dictionary
        data: t.Dict[str, t.Any] = json.loads(json_string)

        # Extract specific keys and their values
        extracted_data: t.Dict[str, t.Any] = {
            "company_name": data.get("company_name", "NO_NAME_FOUND"),
            "employee_size": data.get("employee_size", 0),
            "revenue": data.get("revenue", 0),
            "industry": data.get("industry", "NO_INDUSTRY_FOUND").lower(),
        }

        return extracted_data
    except json.JSONDecodeError:
        dict()


def rank_companies(company_data: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    industry_data: t.Dict[str, t.Any] = standard_industry_data.get(
        company_data.get("industry", {}), {}
    )

    weight_emp_size: float = industry_data.get(
        "weight_emp_size", DEFAULT_WEIGHT_EMP_SIZE
    )
    weight_revenue: float = industry_data.get("weight_revenue", DEFAULT_WEIGHT_REVENUE)
    weight_industry: float = industry_data.get(
        "weight_industry", DEFAULT_WEIGHT_INDUSTRY
    )
    industry_score: float = industry_data.get(
        "industry_score", DEFAULT_WEIGHT_INDUSTRY_SCORE
    )
    max_emp_size: float = industry_data.get("max_emp_size", DEFAULT_MAX_EMP_SIZE)
    max_revenue: float = industry_data.get("max_revenue", DEFAULT_MAX_REVENUE)

    normalized_employee_size: float = normalize(
        company_data["employee_size"], max_emp_size
    )
    normalized_revenue: float = normalize(company_data["revenue"], max_revenue)

    score = (
        weight_emp_size * normalized_employee_size
        + weight_revenue * normalized_revenue
        + weight_industry * industry_score
    )

    company_data["score"] = min(score, 1)
    return company_data


def query_ollama(company_text) -> str:
    data = {
        "model": MODEL,
        "prompt": f"{prompt} {company_text}",
        "stream": False,
    }
    response = requests.post(OLLAMA_URL, headers=headers, json=data)
    if response.status_code == 200:
        try:
            return response.json()["response"]
        except requests.exceptions.JSONDecodeError:
            with open("ollama_response.txt", "w", encoding="utf-8") as file:
                file.write(response.text)
            raise json.JSONDecodeError(
                "Response is not valid JSON. The response has been saved to 'ollama_response.txt'."
            )
    else:
        raise requests.exceptions.RequestException(
            f"Failed to query Ollama: {response.status_code}"
        )


def fetch_wikipedia_page(company_name: str):
    search_url = (
        f"https://en.wikipedia.org/w/rest.php/v1/search/title?q={company_name}&limit=1"
    )
    search_response = requests.get(search_url)

    if search_response.status_code == 200:
        data = search_response.json()
        if len(data["pages"]) > 0:
            first_page = data["pages"][0]
            page_key = first_page["key"]
            logging.info([f"Found Company -> {page_key}"])

            wiki_url = f"https://en.wikipedia.org/wiki/{page_key}"
            wiki_response = requests.get(wiki_url)

            if wiki_response.status_code == 200:
                soup = BeautifulSoup(wiki_response.text, "html.parser")
                company_table = soup.find(
                    "table", {"class": "infobox ib-company vcard"}
                )

                if not company_table:
                    company_table = soup.find("table", {"class": "infobox vcard"})

                if not company_table:
                    raise ValueError("Company information table not found")

                company_info = {}
                rows = company_table.find_all("tr")

                for row in rows:
                    header = row.find("th")
                    data = row.find("td")

                    if header and data:
                        key = header.get_text(strip=True)
                        value = data.get_text(strip=True)
                        company_info[key] = value

                return str(company_info)
            else:
                raise requests.exceptions.RequestException(
                    f"Failed to fetch Wikipedia page: {wiki_response.status_code}"
                )
        else:
            raise LookupError("No results found in search response.")
    else:
        raise requests.exceptions.RequestException(
            f"Search request failed with status code: {search_response.status_code}"
        )


def main():
    if len(sys.argv) < 2:
        print("Usage: python demo.py <company_name>")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)

    company_name: str = sys.argv[1]
    page_content: str = fetch_wikipedia_page(company_name)
    response: str = query_ollama(page_content)
    logging.info([f"LLM Response -> {response}"])

    generated_company_data: t.Dict[str, t.Any] = extract_json_from_response(response)
    logging.info([f"Extracted JSON -> {generated_company_data}"])

    score: float = rank_companies(generated_company_data)
    logging.info([f"Product/Market Fit Score for {company_name}: {score}"])


if __name__ == "__main__":
    main()
