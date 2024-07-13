def filter_persons(persons_result):
    persons_id = []
    persons = []
    for p in persons_result:
        if p.person_id not in persons_id:
            persons_id.append(p.person_id)
            persons.append(p)
        else:
            for per in persons:
                if per.person_id == p.person_id:
                    persons.remove(per)
                    break
            persons.append(p)
    return persons