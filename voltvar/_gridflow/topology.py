def islands(network):
    adjacent={b['id']:set() for b in network['buses']}
    for branch in network['branches']:
        if branch['status']:
            adjacent[branch['from']].add(branch['to']);adjacent[branch['to']].add(branch['from'])
    groups=[];unseen=set(adjacent)
    while unseen:
        group=set();queue=[min(unseen)]
        while queue:
            bus=queue.pop()
            if bus in group:continue
            group.add(bus);queue.extend(adjacent[bus]-group)
        unseen-=group;groups.append(sorted(group))
    return groups

def require_references(network):
    buses={b['id']:b for b in network['buses']}
    groups=islands(network)
    for group in groups:
        count=sum(buses[key]['kind']=='Slack' for key in group)
        if count!=1:raise ValueError(f'Island {group} requires exactly one slack bus; found {count}')
    return groups
