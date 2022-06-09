# def pretty(d, indent=0, string=""):
#     for key, value in d.items():
#         string += ('\t' * indent + str(key) + '\n')
#         if isinstance(value, dict):
#             string += pretty(value, indent + 1, string)
#         else:
#             string += ('\t' * (indent + 1) + str(value))
#     return string
