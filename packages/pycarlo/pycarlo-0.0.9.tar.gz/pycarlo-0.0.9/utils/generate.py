"""
Generates JSON schema from introspection. Use `make generate`.
"""
import json

from sgqlc.endpoint.requests import RequestsEndpoint
from sgqlc.introspection import query, variables
from sgqlc.introspection.__main__ import get_arg_parse

if __name__ == '__main__':
    args = get_arg_parse().parse_args()

    endpoint = RequestsEndpoint(url=args.url, base_headers=dict(args.header))
    data = endpoint(query, variables(include_description=True, include_deprecated=False))

    if data.get('errors'):
        raise SystemExit(f"Failed to retrieve schema with - {data.get('errors')}")
    json.dump(data, args.outfile, sort_keys=True, indent=2, default=str)
