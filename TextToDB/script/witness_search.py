from googlesearch import search

witness_name = "Ealdred"
sawyer_number = "S1507"

results = search(f"https://pase.ac.uk/pase/?list=person {witness_name} {sawyer_number}",advanced=True)

print(next(results))