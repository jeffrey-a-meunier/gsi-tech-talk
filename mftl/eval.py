# type: ignore

# Recursive evaluator
# The only Python features used are:
#  - tuples, creation & access
#  - function definition
#  - function call
#  - if statement
#  - one for loop
#  - assignment statement w/ pattern matching
#  - dictionary, but only as an optimization
#  - print statement

# Without test functions the whole program is < 120 lines

# environment functions

def env_new():
  return ()

def env_lookup(env, key):
  if env == ():
    raise Exception("variable not bound", key)
  (key1, value, env1) = env
  if key1 == key:
    return value
  return env_lookup(env1, key)

def env_bind(key, value, env):
  return (key, value, env)

def env_show(env):
  if env == ():
    return
  (key, value, env1) = env
  print("key =", key, "val =", value)
  env_show(env1)

def env_test():
  x = 100
  y = 200
  z = 300
  env0 = env_new()
  env1 = env_bind('x', x, env0)
  env2 = env_bind('y', y, env1)
  env3 = env_bind('z', z, env2)
  print("env3 =", env3)
  assert x == env_lookup(env3, 'x')
  assert y == env_lookup(env3, 'y')
  assert z == env_lookup(env3, 'z')

# variables

def var_new(id):
  return ('Var', id)

def var_eval(var, env):
  (_, id) = var
  print(">>>> var_eval id =", id, "value =", env_lookup(env, id))
  return (env_lookup(env, id), env)

def var_test():
  env1 = env_bind('x', 100, env_bind('y', 200, env_new()))
  var1 = var_new('y')
  (val, env2) = var_eval(var1, env1)
  assert env1 == env2
  assert val == 200

# let expression

def let_new(id, rhs):
  return ('Let', id, rhs)

def let_eval(let, env):
  (_, id, rhs) = let
  (rhsVal, env1) = evaluate(rhs, env)
  env2 = env_bind(id, rhsVal, env1)
  return (None, env2)

def let_test():
  env1 = env_new()
  let1 = let_new('x', 100)
  (val, env2) = let_eval(let1, env1)
  assert None == val
  assert env_bind('x', 100, env_new()) == env2

# if expression

def if_new(cond, conseq, alt):
  return ('If', cond, conseq, alt)

def if_eval(ifExpr, env):
  (_, cond, conseq, alt) = ifExpr
  (condVal, env1) = evaluate(cond, env)
  if condVal:
    return evaluate(conseq, env1)
  return evaluate(alt, env1)

def if_test():
  env1 = env_new()
  if1 = if_new(True, 100, 200)
  (val, env2) = if_eval(if1, env1)
  print(val, env2)
  assert 100 == val
  assert env_new() == env2

# seq expression

def seq_new(exprs):
  return ('Seq', exprs)

# iterative
def seq_eval(seqExpr, env):
  (_, exprs) = seqExpr
  res = None
  for expr in exprs:
    (res, env) = evaluate(expr, env)
  return (res, env)

# recursive (unused)
# TODO this has an off-by-one problem
def seq_eval_X(seqExpr, env):
  (_, exprs) = seqExpr
  return seq_eval_aux(exprs, len(exprs), 0, None, env)

def seq_eval_aux(exprs, nExprs, n, res, env):
  if n == nExprs:
    return (res, env)
  (_, env1) = evaluate(exprs[n], env)
  return seq_eval_aux(exprs, nExprs, n+1, res, env1)

def seq_test():
  env1 = env_new()
  seq1 = seq_new((let_new('x', 100),
                  let_new('y', 200)))
  (res, env2) = seq_eval(seq1, env1)
  assert None == res
  assert env_bind('y', 200, env_bind('x', 100, env_new())) == env2

# abstraction expression

def fun_new(param, body):
  return ('Fun', param, body)

def fun_eval(fun, env):
  (_, param, body) = fun
  return (('Closure', param, body, env), env)

def fun_test():
  env0 = env_new()
  fun1 = fun_new('x', var_new('x'))
  res = fun_eval(fun1, env0)
  print(res)

# application expression

def app_new(abstr, arg):
  return ('App', abstr, arg)

def app_eval(app, env):
    (_, abstr, arg) = app
    (abstrVal, env1) = evaluate(abstr, env)
    (argVal, env2) = evaluate(arg, env1)
    if isinstance(abstrVal, tuple):
        if abstrVal[0] == 'Closure':
            (_, param, body, lexEnv) = abstrVal
            lexEnv1 = env_bind(param, argVal, lexEnv)
            (res, _) = evaluate(body, lexEnv1)
            return (res, env)  # which env? env, env1, or env2
    raise Exception("object is not applyable", abstr)

def app_test():
  env0 = env_new()
  fun1 = fun_new('x', if_new(var_new('x'), 100, 200))
  app1 = app_new(fun1, True)
  res = app_eval(app1, env0)
  assert (100, ()) == res
  app2 = app_new(fun1, False)
  res = app_eval(app2, env0)
  assert (200, ()) == res

def app_test_lexEnv():
  expr = ('Seq', (('Let', 'x', 100),
                  ('Let', 'y', 200),
                  ('Let', 'f', ('Fun', 'z',
                                ('If', ('Var', 'z'),
                                 ('Var', 'x'),
                                 ('Var', 'y')))),
                  ('Let', 'x', 123),
                  ('Let', 'y', 234),
                  ('App', ('Var', 'f'), True)))
  (val, env1) = evaluate(expr, env_new())
  print("val =", val)
  print("Env:")
  env_show(env1)

# global eval function

evalFuncs = {
  'Var': var_eval,
  'Let': let_eval,
  'If': if_eval,
  'Seq': seq_eval,
  'Fun': fun_eval,
  'App': app_eval
  }

def evaluate(obj, env=env_new()):
  print("Evaluate", obj, "in", env)
  if isinstance(obj, tuple):
    exprType = obj[0]
    evalFunc = evalFuncs[exprType]
    res = evalFunc(obj, env)
    (foo1, foo2) = res
    return res
  return (obj, env)

if __name__ == '__main__':
    app_test_lexEnv()
