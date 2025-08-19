from googlesearch import search

witness_name = "Ealdred"
sawyer_number = "S1507"

results = search(f"site:https://pase.ac.uk/pase/?list=person {witness_name} {sawyer_number}",advanced=True)

# Testing
if False:
    first_result = next(results)
    print(first_result.url)