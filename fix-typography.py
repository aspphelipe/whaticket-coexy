import sys
p = sys.argv[1] if len(sys.argv) > 1 else "/home/deploy/empresa01/frontend/src/components/Settings/Options.js"
f=open(p,"r");c=f.read();f.close()
if 'import { Typography }' not in c:
    old = 'from "@material-ui/core/styles";'
    new = old + '\nimport { Typography } from "@material-ui/core";'
    c = c.replace(old, new, 1)
    f=open(p,"w");f.write(c);f.close()
    print("Typography imported")
else:
    print("Already imported")
