"""
resolve.py: a recursive resolver built using dnspython
"""

import argparse

import dns.message
import dns.name
import dns.query
import dns.rdata
import dns.rdataclass
import dns.rdatatype

FORMATS = (("CNAME", "{alias} is an alias for {name}"),
           ("A", "{name} has address {address}"),
           ("AAAA", "{name} has IPv6 address {address}"),
           ("MX", "{name} mail is handled by {preference} {exchange}"))

# current as of 21 Oct 2022
ROOT_SERVERS = ("198.41.0.4",
                "199.9.14.201",
                "192.33.4.12",
                "199.7.91.13",
                "192.203.230.10",
                "192.5.5.241",
                "192.112.36.4",
                "198.97.190.53",
                "192.36.148.17",
                "192.58.128.30",
                "193.0.14.129",
                "199.7.83.42",
                "202.12.27.33")

CACHE = {}

def collect_results(name: str) -> dict:
    """
    This function parses final answers into the proper data structure that
    print_results requires. The main work is done within the `lookup` function.
    """
    if name in CACHE:
        return CACHE[name]
    full_response = {}
    target_name = dns.name.from_text(name)
    # lookup CNAME
    response = lookup(target_name, dns.rdatatype.CNAME)
    cnames = []
    if response:
        for answers in response.answer:
            for answer in answers:
                cnames.append({"name": answer, "alias": name})
    # lookup A
    response = lookup(target_name, dns.rdatatype.A)
    arecords = []
    if response:
        for answers in response.answer:
            a_name = answers.name
            for answer in answers:
                if answer.rdtype == 1:  # A record
                    arecords.append({"name": a_name, "address": str(answer)})
    # lookup AAAA
    response = lookup(target_name, dns.rdatatype.AAAA)
    aaaarecords = []
    if response:
        for answers in response.answer:
            aaaa_name = answers.name
            for answer in answers:
                if answer.rdtype == 28:  # AAAA record
                    aaaarecords.append({"name": aaaa_name, "address": str(answer)})
    # lookup MX
    response = lookup(target_name, dns.rdatatype.MX)
    mxrecords = []
    if response:
        for answers in response.answer:
            mx_name = answers.name
            for answer in answers:
                if answer.rdtype == 15:  # MX record
                    mxrecords.append({"name": mx_name,
                                    "preference": answer.preference,
                                    "exchange": str(answer.exchange)})

    full_response["CNAME"] = cnames
    full_response["A"] = arecords
    full_response["AAAA"] = aaaarecords
    full_response["MX"] = mxrecords
    CACHE[name] = full_response
    return full_response

def lookup_helper(target_name: dns.name.Name,
           qtype: dns.rdata.Rdata, ip_address) -> dns.message.Message:
    try:
        outbound_query = dns.message.make_query(target_name, qtype)
        response = dns.query.udp(outbound_query, ip_address, 3)       
        if response.answer:
            return response
        elif response.additional:
            for i in response.additional:
                if i[0].rdtype == 1:
                    ip = str(i[0])
                    return lookup_helper(target_name, qtype, ip)
    except:
        return None
def lookup(target_name: dns.name.Name,
           qtype: dns.rdata.Rdata) -> dns.message.Message:
    # Look up for any alias the website goes by, if there are aliases, then
    # RUN the alias on the root servers instead of the target name
    response = None
    for i in ROOT_SERVERS:
        response = lookup_helper(target_name, dns.rdatatype.CNAME, i)
        if response:
            if response.answer:
                break 
    
    if qtype != dns.rdatatype.CNAME:
        if response:
            if len(response.answer) > 0:
                for answers in response.answer:
                    for answer in answers:
                        for i in ROOT_SERVERS:
                            response = lookup_helper(str(answer), qtype, i)
                            if response:
                                if response.answer:
                                    return response
        else:
            for i in ROOT_SERVERS:
                response = lookup_helper(target_name, qtype, i)
                if response:
                    if response.answer:
                        return response
    else:
        return response




def print_results(results: dict) -> None:
    """
    take the results of a `lookup` and print them to the screen like the host
    program would.
    """

    for rtype, fmt_str in FORMATS:
        for result in results.get(rtype, []):
            print(fmt_str.format(**result))


def main():
    """
    if run from the command line, take args and call
    printresults(lookup(hostname))
    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("name", nargs="+",
                                 help="DNS name(s) to look up")
    argument_parser.add_argument("-v", "--verbose",
                                 help="increase output verbosity",
                                 action="store_true")
    program_args = argument_parser.parse_args()
    for a_domain_name in program_args.name:
        print_results(collect_results(a_domain_name))

if __name__ == "__main__":
    main()