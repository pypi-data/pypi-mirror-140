# c_lancet

c_lancet is a static C source code analysis framework. Based on tree-sitter, 
it owns the following characters: 

+ fast speed
+ ease to use since it depends on nothing 
+ rich features based on three levels: project, file, and function

## Examples

```python
# ============ project level ================
from c_lancet.proj import CProj

cp = CProj(proj_path = '../testcase/apps/')
# count number of different file types
print(cp.count_ext(['c', 'h'])) # output: {'c': 75, 'h': 18}
# get all C files under project
c_files = cp.get_ext(['c'])

# ============ file level ================
from c_lancet.file import CFile

cf = CFile(file_path = '../testcase/apps/x509.c')
# get all functions in x509.c
func = cf.get_func()

# ============ function level ================
for _f in func:
    print(_f.get_name())
    print(_f.get_type())
    print(_f.get_para())

```

