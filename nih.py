#%%
import requests
import json

# %%
import requests

def query_nih_reporter_by_criteria(org_name=None, department=None, pi_name=None, additional_criteria=None):
    url = 'https://api.reporter.nih.gov/v2/projects/search'
    criteria = {"criteria": {}}
    
    if org_name:
        criteria["criteria"]["org_names"] = [org_name]
    if department:
        criteria["criteria"]["advanced_text_search"] = {"search_text": department}
    if pi_name:
        criteria["criteria"]["pi_names"] = [{"any_name": pi_name}]
    if additional_criteria:
        for key, value in additional_criteria.items():
            criteria["criteria"][key] = value
    
    params = {
        "offset": 0,
        "limit": 5  # Adjust as needed
    }
    params.update(criteria)
    
    response = requests.post(url, json=params)
    
    if response.status_code == 200:
        grants = response.json().get('results', [])
        for grant in grants:
            print(f"Project Title: {grant.get('project_title')}")
            print(f"PI Name: {grant.get('contact_pi_project_leader')}")
            print(f"Organization: {grant.get('organization', {}).get('org_name')}")
            print(f"Project Start Date: {grant.get('project_start_date')}")
            print(f"Project End Date: {grant.get('project_end_date')}\n")

        return grants
    else:
        print(f"Failed to retrieve data: {response.status_code}")

# Example usage
grants = query_nih_reporter_by_criteria(
    org_name="UNIVERSITY OF CALIFORNIA SAN FRANCISCO",
    department="Neurology",
)

# %%
