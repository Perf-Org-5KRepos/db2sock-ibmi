# description: Generate PaseCliAsync_gen.c
# command:     python gen.py
PaseSqlCli_file = "./gen_cli_template.c"

def parse_sizeme( st ):
   sz = '4'
   if 'SMALL' in st:
     sz = '2'
   elif '*' in st:
     sz = '4'     
   return sz

def parse_star( line ):
  v1 = ""
  v2 = ""
  v3 = ""
  # SQLRETURN * SQLFlinstone
  # 0           1
  split1 = line.split('*')
  if len(split1) > 1:
    v1 = split1[0]
    v2 = "*"
    v3 = split1[1]
  else:
    # SQLRETURN SQLRubble
    # 0         1
    split1 = line.split()
    v1 = split1[0]
    v2 = ""
    v3 = split1[1]
  return [v1.strip(),v2,v3.strip()]


def parse_method( line ):
  # SQLRETURN SQLPrimaryKeys(...)
  # ===func=================1
  split1 = line.split("(")
  func = split1[0]
  # (SQLHSTMT	    hstmt, SQLCHAR *	    szTableQualifier, ...)
  # 1================================argv========================2
  split2 = split1[1].split(")")
  argv = split2[0]
  # SQLRETURN SQLRubble
  # 0         1
  # SQLRETURN * SQLFlinstone
  # 0         1 2
  funcs = parse_star(func)
  # SQLHSTMT	    hstmt, SQLCHAR *	    szTableQualifier, ...
  #                      3                                  3
  split3 = argv.split(",")
  args = []
  for arg in split3:
    # SQLHSTMT hstmt
    # 0        1
    # SQLCHAR * szTableQualifier
    # 0       1 2
    args.append(parse_star(arg))
  return [funcs,args]  

# process PaseSqlCli.c (PASE cmvc)
f = open(PaseSqlCli_file,"r")
g = False
c400 = True
actual_call = ""
chicken_call = ""
line_func = ""
trace_override_libdb400_exp=""
trace_override_libdb400_declare = ""
trace_override_load_dlsym = ""
trace_override_main = ""
trace_async_struct = ""
trace_async_main = ""
trace_async_head_call = ""
trace_async_head_join = ""
trace_special400_main = ""
trace_special400_custom = ""
trace_ILE_struct = ""
trace_ILE_main = ""
trace_ILE_sym = ""
trace_ILE_proto = ""
for line in f:

  # start of SQL function ..
  # int SQLOverrideCCSID400
  # SQLRETURN SQLxxx(
  if "SQLRETURN SQL" in line:
    g = True
    line_func = ""
  if g:
    # throw out change flags and comments 
    # SQLRETURN SQLPrimaryKeys ... /* @08A*/
    #                              0
    line_no_comment = line.split("/")
    split0 = line_no_comment[0]
    line_func += split0
    # end of function ..args..)
    if not ")" in split0:
      continue
    else:
      g = False
  else:   
    continue

  # ---------------
  # parse function
  # ---------------
  parts = parse_method(line_func)
  funcs = parts[0]
  args = parts[1]
  # SQLRETURN SQLPrimaryKeys
  # 0         (1 or 2)
  call_retv = funcs[0] + funcs[1]
  call_name = funcs[2]
  struct_name = call_name + "Struct"
  struct_ile_name = call_name + "IleCallStruct"
  struct_ile_sig = call_name + "IleSigStruct"
  struct_ile_flag = call_name + "Loaded"
  struct_ile_buf = call_name + "Buf"
  struct_ile_ptr = call_name + "Ptr"

  # ---------------
  # custom function (super api)
  # ---------------
  c400 = True
  if "SQL400" in call_name:
    c400 = False
  actual_call = "custom_"
  if c400:
    chicken_call = "libdb400_"
    actual_call = "ILE_"

  # ---------------
  # arguments (params)
  # ---------------
  idx = 0
  comma = ","
  semi = ";"
  argtype1st = ""
  argname1st = ""
  normal_call_types = ""
  normal_call_args = ""
  normal_db400_args = ""
  async_struct_types = " SQLRETURN sqlrc;"
  async_call_args = ""
  async_db400_args = ""
  async_copyin_args = ""
  ILE_struct_sigs = ""
  ILE_struct_types = "ILEarglist_base base;"
  ILE_copyin_args = ""
  for arg in args:
    idx += 1
    if idx == len(args):
      comma = ""
    # SQLHSTMT hstmt
    # 0        1
    # SQLCHAR * szTableQualifier
    # 0       1 2
    argfull = ' '.join(arg)
    argsig = arg[0] + arg[1]
    argname = arg[2]
    if idx == 1:
     argtype1st = arg[0];
     argname1st = arg[2];
    sigile = ''
    ilefull = argfull
    if arg[1] == '*':
      sigile = 'ARG_MEMPTR'
      ilefull = 'ILEpointer' + ' ' + arg[2]
    elif arg[0] == 'PTR':
      sigile = 'ARG_MEMPTR'
      ilefull = 'ILEpointer' + ' ' + arg[2]
    elif arg[0] == 'SQLHWND':
      sigile = 'ARG_MEMPTR'
      ilefull = 'ILEpointer' + ' ' + arg[2]
    elif arg[0] == 'SQLPOINTER':
      sigile = 'ARG_MEMPTR'
      ilefull = 'ILEpointer' + ' ' + arg[2]
    elif arg[0] == 'SQLCHAR':
      sigile = 'ARG_UINT8'
    elif arg[0] == 'SQLWCHAR':
      sigile = 'ARG_UINT8'
    elif arg[0] == 'SQLSMALLINT':
      sigile = 'ARG_INT16'
    elif arg[0] == 'SQLUSMALLINT':
      sigile = 'ARG_UINT16'
    elif arg[0] == 'SQLSMALLINT':
      sigile = 'ARG_INT16'
    elif arg[0] == 'SQLINTEGER':
      sigile = 'ARG_INT32'
    elif arg[0] == 'SQLUINTEGER':
      sigile = 'ARG_UINT32'
    elif arg[0] == 'SQLDOUBLE':
      sigile = 'ARG_FLOAT64'
    elif arg[0] == 'SQLREAL':
      sigile = 'ARG_FLOAT32'
    elif arg[0] == 'HENV':
      sigile = 'ARG_INT32'
    elif arg[0] == 'HDBC':
      sigile = 'ARG_INT32'
    elif arg[0] == 'HSTMT':
      sigile = 'ARG_INT32'
    elif arg[0] == 'HDESC':
      sigile = 'ARG_INT32'
    elif arg[0] == 'SQLHANDLE':
      sigile = 'ARG_INT32'
    elif arg[0] == 'SQLHENV':
      sigile = 'ARG_INT32'
    elif arg[0] == 'SQLHDBC':
      sigile = 'ARG_INT32'
    elif arg[0] == 'SQLHSTMT':
      sigile = 'ARG_INT32'
    elif arg[0] == 'SQLHDESC':
      sigile = 'ARG_INT32'
    elif arg[0] == 'RETCODE':
      sigile = 'ARG_INT32'
    elif arg[0] == 'SQLRETURN':
      sigile = 'ARG_INT32'
    elif arg[0] == 'SFLOAT':
      sigile = 'ARG_FLOAT32'

    # each SQL function override
    # SQLRETURN SQLPrimaryKeys( SQLHSTMT hstmt, SQLCHAR * szTableQualifier, SQLSMALLINT cbTableQualifier, ...
    #                           -------------------------------------------------------------------------
    normal_call_args += ' ' + argfull + comma
    # each SQL function call libdb400
    # sqlrc = libdb400_SQLPrimaryKeys( hstmt, szTableQualifier, cbTableQualifier, ...
    #                                  ------------------------------------------
    normal_db400_args += ' ' + argname + comma
    # static SQLRETURN (*libdb400_SQLPrimaryKeys)(SQLHSTMT,SQLCHAR*,SQLSMALLINT, ...
    #                                             ------------------------------
    normal_call_types += ' ' + argsig + comma

    # ILE call structure
    ILE_struct_types += ' ' + ilefull + semi
    # ILE call signature
    ILE_struct_sigs += ' ' + sigile + comma
    # ILE copyin params
    if sigile == 'ARG_MEMPTR':
      ILE_copyin_args += '  arglist->' + argname + '.s.addr = (address64_t) ' + argname + ";" + "\n"
    else:
      ILE_copyin_args += '  arglist->' + argname + ' = (' + argsig + ') ' + argname + ";" + "\n"

    # each SQL async struct
    # typedef struct SQLPrimaryKeysStruct { SQLRETURN sqlrc; SQLHSTMT hstmt;  ...
    #                                       --------------------------------
    async_struct_types += ' ' + argfull + semi
    # each SQL asyn call libdb400
    # myptr->sqlrc = libdb400_SQLPrimaryKeys( myptr->hstmt, myptr->szTableQualifier, myptr->cbTableQualifier, ...
    #                                  ------------------------------------------
    async_db400_args += ' myptr->' + argname + comma
    # each SQL asyn copyin parms
    # myptr->hstmt = hstmt;
    # myptr->szTableQualifier = szTableQualifier; 
    # myptr->cbTableQualifier = cbTableQualifier; 
    # ...
    #                                  ------------------------------------------
    async_copyin_args += '  myptr->' + argname + " = " + argname + ";" + "\n"


  # ===============================================
  # non-async SQL interfaces with lock added
  # ===============================================

  if c400:
    # declare dlsym call each SQL function
    # static SQLRETURN (*libdb400_SQLAllocEnv)(SQLHENV*);
    trace_override_libdb400_declare += "static SQLRETURN (*" + "libdb400_" + call_name + ')(' + normal_call_types + ' );' + "\n"
  
    # init dlsym locate each SQL function in libdb400.a 
    # void load_dlsym() {
    #   libdb400_SQLAllocEnv = dlsym(dlhandle, "SQLAllocEnv");
    # }
    trace_override_load_dlsym += "  libdb400_" + call_name + ' = dlsym(dlhandle, "'+ call_name +'");' + "\n"
  else:
    # each SQL400 function special (header)
    # SQLRETURN SQL400Environment( SQLINTEGER * ohnd, SQLPOINTER  options )
    #
    trace_special400_main += call_retv + ' ' + call_name + '(' + normal_call_args + ' );' + "\n"
    trace_special400_custom += call_retv + ' ' + "custom_" + call_name + '(' + normal_call_args + ' );' + "\n"

  # export special libdb400.a
  trace_override_libdb400_exp += call_name + "\n"

  # each SQL function override
  # SQLRETURN SQLAllocEnv( SQLHENV * phenv )
  # { 
  # }
  trace_override_main += call_retv + ' ' + call_name + '(' + normal_call_args + ' )' + "\n"
  trace_override_main += "{" + "\n"
  trace_override_main += "  SQLRETURN sqlrc = SQL_SUCCESS;" + "\n"
  trace_override_main += "  if (i_am_big_chicken_flag) {" + "\n"
  trace_override_main += "    init_dlsym();" + "\n"
  trace_override_main += "  }" + "\n"
  # SQLRETURN SQLAllocEnv ( SQLHENV * phenv );
  if call_name == "SQLAllocEnv":
    trace_override_main += "  init_lock();" + "\n"
    trace_override_main += "  if (i_am_big_chicken_flag) {" + "\n"
    trace_override_main += "    sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "  } else {" + "\n"
    trace_override_main += "    sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "  }" + "\n"
    trace_override_main += "  if (sqlrc == SQL_SUCCESS) {" + "\n"
    trace_override_main += "    init_table_ctor(*phenv, *phenv);" + "\n"
    trace_override_main += "  }" + "\n"
    trace_override_main += "  init_unlock();" + "\n"
  # SQLRETURN SQLAllocConnect ( SQLHENV  henv, SQLHDBC * phdbc );
  elif call_name == "SQLAllocConnect":
    trace_override_main += "  init_lock();" + "\n"
    trace_override_main += "  if (i_am_big_chicken_flag) {" + "\n"
    trace_override_main += "    sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "  } else {" + "\n"
    trace_override_main += "    sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "  }" + "\n"
    trace_override_main += "  if (sqlrc == SQL_SUCCESS) {" + "\n"
    trace_override_main += "    init_table_ctor(*phdbc, *phdbc);" + "\n"
    trace_override_main += "  }" + "\n"
    trace_override_main += "  init_unlock();" + "\n"
  # SQLRETURN SQLAllocStmt ( SQLHDBC  hdbc, SQLHSTMT * phstmt );
  elif call_name == "SQLAllocStmt":
    trace_override_main += "  init_lock();" + "\n"
    trace_override_main += "  if (i_am_big_chicken_flag) {" + "\n"
    trace_override_main += "    sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "  } else {" + "\n"
    trace_override_main += "    sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "  }" + "\n"
    trace_override_main += "  if (sqlrc == SQL_SUCCESS) {" + "\n"
    trace_override_main += "    init_table_ctor(*phstmt, hdbc);" + "\n"
    trace_override_main += "  }" + "\n"
    trace_override_main += "  init_unlock();" + "\n"
  # SQLRETURN SQLAllocHandle ( SQLSMALLINT  htype, SQLINTEGER  ihnd, SQLINTEGER * ohnd );
  elif call_name == "SQLAllocHandle":
    trace_override_main += "  switch (htype) {" + "\n"
    trace_override_main += "  case SQL_HANDLE_ENV:" + "\n"
    trace_override_main += "    init_lock();" + "\n"
    trace_override_main += "    if (i_am_big_chicken_flag) {" + "\n"
    trace_override_main += "      sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "    } else {" + "\n"
    trace_override_main += "      sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "    }" + "\n"
    trace_override_main += "    if (sqlrc == SQL_SUCCESS) {" + "\n"
    trace_override_main += "      init_table_ctor(*ohnd, *ohnd);" + "\n"
    trace_override_main += "    }" + "\n"
    trace_override_main += "    init_unlock();" + "\n"
    trace_override_main += "    break;" + "\n"
    trace_override_main += "  case SQL_HANDLE_DBC:" + "\n"
    trace_override_main += "    init_lock();" + "\n"
    trace_override_main += "    if (i_am_big_chicken_flag) {" + "\n"
    trace_override_main += "      sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "    } else {" + "\n"
    trace_override_main += "      sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "    }" + "\n"
    trace_override_main += "    if (sqlrc == SQL_SUCCESS) {" + "\n"
    trace_override_main += "      init_table_ctor(*ohnd, *ohnd);" + "\n"
    trace_override_main += "    }" + "\n"
    trace_override_main += "    init_unlock();" + "\n"
    trace_override_main += "    break;" + "\n"
    trace_override_main += "  case SQL_HANDLE_STMT:" + "\n"
    trace_override_main += "    init_lock();" + "\n"
    trace_override_main += "    if (i_am_big_chicken_flag) {" + "\n"
    trace_override_main += "      sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "    } else {" + "\n"
    trace_override_main += "      sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "    }" + "\n"
    trace_override_main += "    if (sqlrc == SQL_SUCCESS) {" + "\n"
    trace_override_main += "      init_table_ctor(*ohnd, ihnd);" + "\n"
    trace_override_main += "    }" + "\n"
    trace_override_main += "    init_unlock();" + "\n"
    trace_override_main += "    break;" + "\n"
    trace_override_main += "  case SQL_HANDLE_DESC:" + "\n"
    trace_override_main += "    init_lock();" + "\n"
    trace_override_main += "    if (i_am_big_chicken_flag) {" + "\n"
    trace_override_main += "      sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "    } else {" + "\n"
    trace_override_main += "      sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "    }" + "\n"
    trace_override_main += "    if (sqlrc == SQL_SUCCESS) {" + "\n"
    trace_override_main += "      init_table_ctor(*ohnd, ihnd);" + "\n"
    trace_override_main += "    }" + "\n"
    trace_override_main += "    init_unlock();" + "\n"
    trace_override_main += "    break;" + "\n"
    trace_override_main += "  }" + "\n"
  # SQLRETURN SQLFreeEnv ( SQLHENV  henv );
  elif call_name == "SQLFreeEnv":
    trace_override_main += "  init_lock();" + "\n"
    trace_override_main += "  if (i_am_big_chicken_flag) {" + "\n"
    trace_override_main += "    sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "  } else {" + "\n"
    trace_override_main += "    sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "  }" + "\n"
    trace_override_main += "  init_unlock();" + "\n"
  # SQLRETURN SQLFreeConnect ( SQLHDBC  hdbc );
  elif call_name == "SQLFreeConnect":
    trace_override_main += "  init_lock();" + "\n"
    trace_override_main += "  if (i_am_big_chicken_flag) {" + "\n"
    trace_override_main += "    sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "  } else {" + "\n"
    trace_override_main += "    sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "  }" + "\n"
    trace_override_main += "  if (sqlrc == SQL_SUCCESS) {" + "\n"
    trace_override_main += "    init_table_dtor(hdbc);" + "\n"
    trace_override_main += "  }" + "\n"
    trace_override_main += "  init_unlock();" + "\n"
  # SQLRETURN SQLFreeStmt ( SQLHSTMT  hstmt, SQLSMALLINT  fOption );
  elif call_name == "SQLFreeStmt":
    trace_override_main += "  init_lock();" + "\n"
    trace_override_main += "  if (i_am_big_chicken_flag) {" + "\n"
    trace_override_main += "    sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "  } else {" + "\n"
    trace_override_main += "    sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "  }" + "\n"
    trace_override_main += "  if (sqlrc == SQL_SUCCESS) {" + "\n"
    trace_override_main += "    init_table_dtor(hstmt);" + "\n"
    trace_override_main += "  }" + "\n"
    trace_override_main += "  init_unlock();" + "\n"
  # SQLRETURN SQLFreeHandle ( SQLSMALLINT  htype, SQLINTEGER  hndl );
  elif call_name == "SQLFreeHandle":
    trace_override_main += "  switch (htype) {" + "\n"
    trace_override_main += "  case SQL_HANDLE_ENV:" + "\n"
    trace_override_main += "    init_lock();" + "\n"
    trace_override_main += "    if (i_am_big_chicken_flag) {" + "\n"
    trace_override_main += "      sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "    } else {" + "\n"
    trace_override_main += "      sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "    }" + "\n"
    trace_override_main += "    init_unlock();" + "\n"
    trace_override_main += "    break;" + "\n"
    trace_override_main += "  case SQL_HANDLE_DBC:" + "\n"
    trace_override_main += "    init_lock();" + "\n"
    trace_override_main += "    if (i_am_big_chicken_flag) {" + "\n"
    trace_override_main += "      sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "    } else {" + "\n"
    trace_override_main += "      sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "    }" + "\n"
    trace_override_main += "    if (sqlrc == SQL_SUCCESS) {" + "\n"
    trace_override_main += "      init_table_dtor(hndl);" + "\n"
    trace_override_main += "    }" + "\n"
    trace_override_main += "    init_unlock();" + "\n"
    trace_override_main += "    break;" + "\n"
    trace_override_main += "  case SQL_HANDLE_STMT:" + "\n"
    trace_override_main += "    init_lock();" + "\n"
    trace_override_main += "    if (i_am_big_chicken_flag) {" + "\n"
    trace_override_main += "      sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "    } else {" + "\n"
    trace_override_main += "      sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "    }" + "\n"
    trace_override_main += "    if (sqlrc == SQL_SUCCESS) {" + "\n"
    trace_override_main += "      init_table_dtor(hndl);" + "\n"
    trace_override_main += "    }" + "\n"
    trace_override_main += "    init_unlock();" + "\n"
    trace_override_main += "    break;" + "\n"
    trace_override_main += "  case SQL_HANDLE_DESC:" + "\n"
    trace_override_main += "    init_lock();" + "\n"
    trace_override_main += "    if (i_am_big_chicken_flag) {" + "\n"
    trace_override_main += "      sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "    } else {" + "\n"
    trace_override_main += "      sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
    trace_override_main += "    }" + "\n"
    trace_override_main += "    if (sqlrc == SQL_SUCCESS) {" + "\n"
    trace_override_main += "      init_table_dtor(hndl);" + "\n"
    trace_override_main += "    }" + "\n"
    trace_override_main += "    init_unlock();" + "\n"
    trace_override_main += "    break;" + "\n"
    trace_override_main += "  }" + "\n"
  else:
    if argtype1st == "SQLHENV":
      if actual_call == "custom_":
        trace_override_main += "  sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
      else:
        trace_override_main += "  if (i_am_big_chicken_flag) {" + "\n"
        trace_override_main += "    sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
        trace_override_main += "  } else {" + "\n"
        trace_override_main += "    sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
        trace_override_main += "  }" + "\n"
    elif argtype1st == "SQLHDBC":
      trace_override_main += "  init_table_lock(" + argname1st + ", 0);" + "\n"
      if actual_call == "custom_":
        trace_override_main += "  sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
      else:
        trace_override_main += "  if (i_am_big_chicken_flag) {" + "\n"
        trace_override_main += "    sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
        trace_override_main += "  } else {" + "\n"
        trace_override_main += "    sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
        trace_override_main += "  }" + "\n"
      trace_override_main += "  init_table_unlock(" + argname1st + ", 0);" + "\n"
    elif argtype1st == "SQLHSTMT":
      trace_override_main += "  init_table_lock(" + argname1st + ", 1);" + "\n"
      if actual_call == "custom_":
        trace_override_main += "  sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
      else:
        trace_override_main += "  if (i_am_big_chicken_flag) {" + "\n"
        trace_override_main += "    sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
        trace_override_main += "  } else {" + "\n"
        trace_override_main += "    sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
        trace_override_main += "  }" + "\n"
      trace_override_main += "  init_table_unlock(" + argname1st + ", 1);" + "\n"
    elif argtype1st == "SQLHDESC":
      trace_override_main += "  init_table_lock(" + argname1st + ", 1);" + "\n"
      if actual_call == "custom_":
        trace_override_main += "  sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
      else:
        trace_override_main += "  if (i_am_big_chicken_flag) {" + "\n"
        trace_override_main += "    sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
        trace_override_main += "  } else {" + "\n"
        trace_override_main += "    sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
        trace_override_main += "  }" + "\n"
      trace_override_main += "  init_table_unlock(" + argname1st + ", 1);" + "\n"
    else:
      if actual_call == "custom_":
        trace_override_main += "  sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
      else:
        trace_override_main += "  if (i_am_big_chicken_flag) {" + "\n"
        trace_override_main += "    sqlrc = " + chicken_call + call_name + '(' + normal_db400_args + ' );' + "\n"
        trace_override_main += "  } else {" + "\n"
        trace_override_main += "    sqlrc = " + actual_call + call_name + '(' + normal_db400_args + ' );' + "\n"
        trace_override_main += "  }" + "\n"
  # common code
  trace_override_main += "  return sqlrc;" + "\n"
  trace_override_main += "}" + "\n"


  # ===============================================
  # ILE call
  # ===============================================

  # ILE
  if c400:
    trace_ILE_proto += call_retv + ' ILE_' + call_name + '(' + normal_call_args + ' );' + "\n"

    trace_ILE_struct += 'typedef struct ' + struct_ile_name + ' {' + ILE_struct_types + ' } ' + struct_ile_name + ';'  + "\n";

    trace_ILE_sym  += 'SQLINTEGER ' + struct_ile_flag + ';' + "\n"
    trace_ILE_sym  += 'SQLCHAR ' + struct_ile_buf + '[132];' + "\n"

    trace_ILE_main += call_retv + ' ILE_' + call_name + '(' + normal_call_args + ' )' + "\n"
    trace_ILE_main += '{' + "\n"
    trace_ILE_main += '  int rc = 0;' + "\n"
    trace_ILE_main += '  SQLRETURN sqlrc = SQL_SUCCESS;' + "\n"
    trace_ILE_main += '  int actMark = 0;' + "\n"
    trace_ILE_main += '  char * ileSymPtr = (char *) NULL;' + "\n"
    trace_ILE_main += '  ' + struct_ile_name + ' * arglist = (' + struct_ile_name + ' *) NULL;' + "\n"
    trace_ILE_main += '  char buffer[ sizeof(' + struct_ile_name + ') + 16 ];' + "\n"
    trace_ILE_main += '  static arg_type_t ' + struct_ile_sig + '[] = {' + ILE_struct_sigs + ', ARG_END };'  + "\n";
    trace_ILE_main += '  arglist = (' + struct_ile_name + ' *)ROUND_QUAD(buffer);' + "\n"
    trace_ILE_main += '  ileSymPtr = (char *)ROUND_QUAD(&' + struct_ile_buf + ');' +  "\n"
    trace_ILE_main += '  memset(buffer,0,sizeof(buffer));' +  "\n"
    trace_ILE_main += '  if (!db2_cli_srvpgm_mark) {' +  "\n"
    trace_ILE_main += '    actMark = _ILELOAD(DB2CLISRVPGM, ILELOAD_LIBOBJ);' +  "\n"
    trace_ILE_main += '    if (actMark < 0) {' + "\n"
    trace_ILE_main += '      return SQL_ERROR;' + "\n"
    trace_ILE_main += '    }' + "\n"
    trace_ILE_main += '    db2_cli_srvpgm_mark = actMark;' +  "\n"
    trace_ILE_main += '  }' + "\n"
    trace_ILE_main += '  if (!'+ struct_ile_flag +') {' +  "\n"
    trace_ILE_main += '    rc = _ILESYM(ileSymPtr, db2_cli_srvpgm_mark, "' + call_name + '");' +  "\n"
    trace_ILE_main += '    if (rc < 0) {' + "\n"
    trace_ILE_main += '      return SQL_ERROR;' + "\n"
    trace_ILE_main += '    }' + "\n"
    trace_ILE_main += '    ' + struct_ile_flag + ' = 1;' +  "\n"
    trace_ILE_main += '  }' + "\n"
    trace_ILE_main += ILE_copyin_args
    trace_ILE_main += '  rc = _ILECALL(ileSymPtr, &arglist->base, ' + struct_ile_sig + ', RESULT_INT32);' +  "\n"
    trace_ILE_main += '  if (rc != ILECALL_NOERROR) {' + "\n"
    trace_ILE_main += '    return SQL_ERROR;' + "\n"
    trace_ILE_main += '  }' + "\n"
    trace_ILE_main += '  return arglist->base.result.s_int32.r_int32;' + "\n"
    trace_ILE_main += '}' + "\n"

  # ===============================================
  # NO async SQL interfaces with thread
  # ===============================================
  # SQLRETURN SQLAllocEnv ( SQLHENV * phenv );
  if call_name == "SQLAllocEnv":
    continue
  # SQLRETURN SQLAllocConnect ( SQLHENV  henv, SQLHDBC * phdbc );
  elif call_name == "SQLAllocConnect":
    continue
  # SQLRETURN SQLAllocStmt ( SQLHDBC  hdbc, SQLHSTMT * phstmt );
  elif call_name == "SQLAllocStmt":
    continue
  # SQLRETURN SQLAllocHandle ( SQLSMALLINT  htype, SQLINTEGER  ihnd, SQLINTEGER * ohnd );
  elif call_name == "SQLAllocHandle":
    continue
  # SQLRETURN SQLFreeEnv ( SQLHENV  henv );
  elif call_name == "SQLFreeEnv":
    continue
  # SQLRETURN SQLFreeConnect ( SQLHDBC  hdbc );
  elif call_name == "SQLFreeConnect":
    continue
  # SQLRETURN SQLFreeStmt ( SQLHSTMT  hstmt, SQLSMALLINT  fOption );
  elif call_name == "SQLFreeStmt":
    continue
  # SQLRETURN SQLFreeHandle ( SQLSMALLINT  htype, SQLINTEGER  hndl );
  elif call_name == "SQLFreeHandle":
    continue


  # ===============================================
  # async SQL interfaces with thread
  # ===============================================
  async_call_args = normal_call_args + ', void * callback'
  async_struct_types += ' void * callback;'
  async_copyin_args += '  myptr->callback = callback;' + "\n"

  # each SQL function async (header)
  # SQLRETURN SQLSpecialColumnsAsync ( SQLHSTMT  hstmt, SQLSMALLINT  fColType, ... , void * callback )
  # void (*callback)(SQLSpecialColumnsStruct* )
  # SQLSpecialColumnsStruct * SQLSpecialColumnsJoin (pthread_t tid, SQLINTEGER flag)
  #
  trace_async_callback_comment = '/* void ' + call_name + 'Callback(' + struct_name + '* ); */'
  trace_async_head_call += 'pthread_t ' + call_name + 'Async (' + async_call_args + ' );' + "\n"
  trace_async_head_join +=  trace_async_callback_comment + "\n"
  trace_async_head_join += struct_name + ' * ' + call_name + 'Join (pthread_t tid, SQLINTEGER flag);' + "\n"

  # export special libdb400.a
  trace_override_libdb400_exp += call_name + 'Async' + "\n"
  trace_override_libdb400_exp += call_name + 'Join' + "\n"


  # each SQL function async
  # typedef struct SQLAllocEnvStruct {
  #   SQLRETURN sqlrc;
  #   SQLHENV * phenv;
  # } SQLAllocEnvStruct;
  #
  #
  trace_async_struct += 'typedef struct ' + struct_name + ' {' + async_struct_types + ' } ' + struct_name + ';'  + "\n";


  # each SQL function async
  # void * SQLAllocEnvThread(void *ptr)
  # {
  #   void (*callback)(SQLSpecialColumnsStruct* )
  # }
  trace_async_main += 'void * ' + call_name + 'Thread (void *ptr)' + "\n"
  trace_async_main += "{" + "\n"
  trace_async_main += '  ' + struct_name + ' * myptr = (' + struct_name + ' *) ptr;' + "\n"
  if argtype1st == "SQLHENV":
    trace_async_main += "  /* not lock */" + "\n"
  elif argtype1st == "SQLHDBC":
    trace_async_main += "  init_table_lock(myptr->" + argname1st + ", 0);" + "\n"
  elif argtype1st == "SQLHSTMT":
    trace_async_main += "  init_table_lock(myptr->" + argname1st + ", 1);" + "\n"
  elif argtype1st == "SQLHDESC":
    trace_async_main += "  init_table_lock(myptr->" + argname1st + ", 1);" + "\n"
  if actual_call == "custom_":
    trace_async_main += "  myptr->sqlrc = " + actual_call + call_name + '(' + async_db400_args + ' );' + "\n"
  else:
    trace_async_main += "  if (i_am_big_chicken_flag) {" + "\n"
    trace_async_main += "    myptr->sqlrc = " + chicken_call + call_name + '(' + async_db400_args + ' );' + "\n"
    trace_async_main += "  } else {" + "\n"
    trace_async_main += "    myptr->sqlrc = " + actual_call + call_name + '(' + async_db400_args + ' );' + "\n"
    trace_async_main += "  }" + "\n"
  if argtype1st == "SQLHENV":
    trace_async_main += "  /* not lock */" + "\n"
  elif argtype1st == "SQLHDBC":
    trace_async_main += "  init_table_unlock(myptr->" + argname1st + ", 0);" + "\n"
  elif argtype1st == "SQLHSTMT":
    trace_async_main += "  init_table_unlock(myptr->" + argname1st + ", 1);" + "\n"
  elif argtype1st == "SQLHDESC":
    trace_async_main += "  init_table_unlock(myptr->" + argname1st + ", 1);" + "\n"
  trace_async_main += '  ' + trace_async_callback_comment + "\n"
  trace_async_main += '  if (myptr->callback) {' + "\n"
  trace_async_main += '    void (*ptrFunc)(' + struct_name + '* ) = myptr->callback;' + "\n"
  trace_async_main += '    ptrFunc( myptr );' + "\n"
  trace_async_main += "  }" + "\n"
  trace_async_main += "  pthread_exit((void *)myptr);" + "\n"
  trace_async_main += "}" + "\n"

  # each SQL function async
  # pthread_t SQLSpecialColumnsAsync ( SQLHSTMT  hstmt, SQLSMALLINT  fColType, ... , void * callback )
  # { 
  # }
  trace_async_main += 'pthread_t ' + call_name + 'Async (' + async_call_args + ' )' + "\n"
  trace_async_main += '{' + "\n"
  trace_async_main += '  int rc = 0;' + "\n"
  trace_async_main += '  pthread_t tid = 0;' + "\n"
  trace_async_main += '  ' + struct_name + ' * myptr = (' + struct_name + ' *) malloc(sizeof(' + struct_name + '));' + "\n"
  trace_async_main += "  if (i_am_big_chicken_flag) {" + "\n"
  trace_async_main += "    init_dlsym();" + "\n"
  trace_async_main += "  }" + "\n"
  trace_async_main += '  myptr->sqlrc = SQL_SUCCESS;' + "\n"
  trace_async_main += async_copyin_args
  trace_async_main += '  rc = pthread_create(&tid, NULL, '+ call_name + 'Thread, (void *)myptr);' + "\n"
  trace_async_main += '  return tid;' + "\n"
  trace_async_main += '}' + "\n"

  # each SQL function async
  # SQLSpecialColumnsStruct * SQLSpecialColumnsJoin (pthread_t tid, SQLINTEGER flag)
  # { 
  # }
  trace_async_main += struct_name + ' * ' + call_name + 'Join (pthread_t tid, SQLINTEGER flag)' + "\n"
  trace_async_main += "{" + "\n"
  trace_async_main += "  " + struct_name + " * myptr = (" + struct_name + " *) NULL;" + "\n"
  trace_async_main += "  int active = 0;" + "\n"
  trace_async_main += "  if (i_am_big_chicken_flag) {" + "\n"
  trace_async_main += "    init_dlsym();" + "\n"
  trace_async_main += "  }" + "\n"
  if argtype1st == "SQLHENV":
    trace_async_main += "  /* not lock */" + "\n"
  elif argtype1st == "SQLHDBC":
    trace_async_main += "  active = init_table_in_progress(myptr->" + argname1st + ", 0);" + "\n"
  elif argtype1st == "SQLHSTMT":
    trace_async_main += "  active = init_table_in_progress(myptr->" + argname1st + ", 1);" + "\n"
  elif argtype1st == "SQLHDESC":
    trace_async_main += "  active = init_table_in_progress(myptr->" + argname1st + ", 1);" + "\n"
  trace_async_main += "  if (flag == SQL400_FLAG_JOIN_WAIT || !active) {" + "\n"
  trace_async_main += "    pthread_join(tid,(void**)&myptr);" + "\n"
  trace_async_main += "  } else {" + "\n"
  trace_async_main += "    return (" + struct_name + " *) NULL;" + "\n"
  trace_async_main += "  }" + "\n"
  trace_async_main += "  return myptr;" + "\n"
  trace_async_main += "}" + "\n"


# write PaseCliAsync_gen.c (no h file)
trace_incl = ""
trace_incl += "#include <stdio.h>" + "\n"
trace_incl += "#include <stdlib.h>" + "\n"
trace_incl += "#include <unistd.h>" + "\n"
trace_incl += "#include <dlfcn.h>" + "\n"
trace_incl += "#include <sqlcli1.h>" + "\n"
trace_incl += "#include <as400_types.h>" + "\n"
trace_incl += "#include <as400_protos.h>" + "\n"
trace_incl += '#include "PaseCliInit.h"' + "\n"
trace_incl += '#include "PaseCliAsync.h"' + "\n"
trace_incl += "" + "\n"
trace_incl += 'int i_am_big_chicken_flag;' + "\n"
trace_incl += 'int db2_cli_srvpgm_mark;' + "\n"
trace_incl += '#define DB2CLISRVPGM "QSYS/QSQCLI"' + "\n"
trace_incl += '#define ROUND_QUAD(x) (((size_t)(x) + 0xf) & ~0xf)' + "\n"
trace_incl += "" + "\n"
trace_incl += "/* ILE call                          */" + "\n"
trace_incl += "" + "\n"
trace_incl += trace_ILE_proto
trace_incl += "" + "\n"
trace_incl += "/* ILE call structures               */" + "\n"
trace_incl += "" + "\n"
trace_incl += trace_ILE_struct + "\n"
trace_incl += "" + "\n"
trace_incl += "/* special SQL400 aggregate functions */" + "\n"
trace_incl += "/* do common work for language driver */" + "\n"
trace_incl += "/* composite calls to CLI also async  */" + "\n"
trace_incl += "" + "\n"
trace_incl += trace_special400_custom
trace_incl += "" + "\n"
trace_incl += trace_override_libdb400_declare + "\n"
trace_incl += "" + "\n"
trace_incl += trace_ILE_sym
trace_incl += "" + "\n"
trace_incl += trace_ILE_main
trace_incl += "" + "\n"
trace_incl += "void load_dlsym() {" + "\n"
trace_incl += trace_override_load_dlsym + "\n"
trace_incl +=  "}" + "\n"
trace_incl += "" + "\n"
trace_all = ""
trace_all += trace_incl
trace_all += trace_override_main
trace_all += trace_async_main
with open("PaseCliAsync_gen.c", "w") as text_file:
    text_file.write(trace_all)


trace_incl = ""
trace_incl += "#include <stdio.h>" + "\n"
trace_incl += "#include <stdlib.h>" + "\n"
trace_incl += "#include <unistd.h>" + "\n"
trace_incl += "#include <dlfcn.h>" + "\n"
trace_incl += "#include <sqlcli1.h>" + "\n"
trace_incl += "#include <as400_types.h>" + "\n"
trace_incl += "#include <as400_protos.h>" + "\n"
trace_incl += "" + "\n"
trace_all = ""
trace_all += '#ifndef _PASECLIASYNC_H' + "\n"
trace_all += '#define _PASECLIASYNC_H' + "\n"
trace_all += "" + "\n"
trace_all += trace_incl
trace_all += "" + "\n"
trace_all += "/* special SQL400 aggregate functions */" + "\n"
trace_all += "/* do common work for language driver */" + "\n"
trace_all += "/* composite calls to CLI also async  */" + "\n"
trace_all += "" + "\n"
trace_all += '#define SQL400_FLAG_JOIN_WAIT 0' + "\n"
trace_all += '#define SQL400_FLAG_JOIN_NO_WAIT 1' + "\n"
trace_all += "" + "\n"
trace_all += '/* Use:' + "\n"
trace_all += ' * SQL400Environment' + "\n"
trace_all += ' * ' + "\n"
trace_all += ' * ok, unicode please ...' + "\n"
trace_all += ' * ' + "\n"
trace_all += ' * UTF8 normal interfaces (default 1208):' + "\n"
trace_all += ' *   int ccsid = 1208;' + "\n"
trace_all += ' *   env attr SQL400_ATTR_PASE_CCSID &ccsid -- set pase ccsid' + "\n"
trace_all += ' *   if ccsid == 1208:' + "\n"
trace_all += ' *     env attr SQL_ATTR_UTF8 &true -- no conversion required by PASE' + "\n"
trace_all += ' * ' + "\n"
trace_all += ' * UTF16 wide interfaces:' + "\n"
trace_all += ' *   So, database exotic ebcdic column and PASE binds c type as WVARCHAR/WCHAR output is UTF16?' + "\n"
trace_all += ' *   Yes, the database will do the conversion from EBCDIC to UTF16 for data bound as WVARCHAR/WCHAR.' + "\n"
trace_all += ' *   not sure about DBCLOB -- I want to guess that is bound as UTF-16, not 100% sure.' + "\n"
trace_all += ' * ' + "\n"
trace_all += ' * IF your data not UTF-8 or UTF-16, use following interfaces to convert.' + "\n"
trace_all += ' *   SQL400ToUtf8    -- use before passing to CLI normal interfaces' + "\n"
trace_all += ' *   SQL400FromUtf8  -- use return output normal CLI (if needed)' + "\n"
trace_all += ' *   SQL400ToUtf16   -- use before passing to CLI wide interfaces' + "\n"
trace_all += ' *   SQL400FromUtf16 -- use return output wide CLI (if needed)' + "\n"
trace_all += ' * ' + "\n"
trace_all += ' */' + "\n"
trace_all += '#define SQL400_ATTR_PASE_CCSID 10011' + "\n"
trace_all += '/* Use:' + "\n"
trace_all += ' *   SQL400Environment ( ..., SQLPOINTER  options )' + "\n"
trace_all += ' *   SQL400Connect ( ..., SQLPOINTER  options )' + "\n"
trace_all += ' *   SQL400SetAttr ( ..., SQLPOINTER  options )' + "\n"
trace_all += ' * CTOR:' + "\n"
trace_all += ' *   SQL400AddAttr' + "\n"
trace_all += ' * Struct:' + "\n"
trace_all += ' *   SQL400AttrStruct' + "\n"
trace_all += ' *     e - EnvAttr' + "\n"
trace_all += ' *     c - ConnectAttr' + "\n"
trace_all += ' *     s - StmtAttr' + "\n"
trace_all += ' *     o - StmtOption' + "\n"
trace_all += ' */' + "\n"
trace_all += '#define SQL400_ONERR_CONT 1' + "\n"
trace_all += '#define SQL400_ONERR_STOP 2' + "\n"
trace_all += '#define SQL400_FLAG_IMMED 0' + "\n"
trace_all += '#define SQL400_FLAG_PRE_CONNECT 1' + "\n"
trace_all += '#define SQL400_FLAG_POST_CONNECT 2' + "\n"
trace_all += 'typedef struct SQL400AttrStruct {' + "\n"
trace_all += ' SQLINTEGER scope;   /*      - scope  - SQL_HANDLE_ENV|DBC|SRTMT|DESC */' + "\n"
trace_all += ' SQLHANDLE  hndl;    /* ecso - hndl   - CLI handle                    */' + "\n"
trace_all += ' SQLINTEGER attrib;  /* ecso - attrib - CLI attribute                 */' + "\n"
trace_all += ' SQLPOINTER vParam;  /* ecso - vParam - ptr to CLI value              */' + "\n"
trace_all += ' SQLINTEGER inlen;   /* ecs  - inlen  - len CLI value (string)        */' + "\n"
trace_all += ' SQLINTEGER sqlrc;   /*      - sqlrc  - sql return code               */' + "\n"
trace_all += ' SQLINTEGER onerr;   /*      - onerr  - SQL400_ONERR_xxx              */' + "\n"
trace_all += ' SQLINTEGER flag;    /*      - flag   - SQL400_FLAG_xxx               */' + "\n"
trace_all += '} SQL400AttrStruct;' + "\n"
trace_all += '/* Use:' + "\n"
trace_all += ' *   SQL400Execute( ..., SQLPOINTER parms, SQLPOINTER desc_parms)' + "\n"
trace_all += ' *   SQL400Fetch (..., SQLPOINTER desc_cols)' + "\n"
trace_all += ' * CTOR:' + "\n"
trace_all += ' *   SQL400Describe' + "\n"
trace_all += ' *   SQL400AddCVar' + "\n"
trace_all += ' * Struct:' + "\n"
trace_all += ' *   SQL400ParamStruct' + "\n"
trace_all += ' *   SQL400DescribeStruct' + "\n"
trace_all += ' *     p - SQLDescribeParam' + "\n"
trace_all += ' *     c - SQLDescribeCol' + "\n"
trace_all += ' */' + "\n"
trace_all += '#define SQL400_DESC_PARM 0' + "\n"
trace_all += '#define SQL400_DESC_COL  1' + "\n"
trace_all += '#define SQL400_PARM_IO_FILE 42' + "\n"
trace_all += 'typedef struct SQL400ParamStruct {' + "\n"
trace_all += ' SQLSMALLINT icol;            /* icol         - param number      (in)  */' + "\n"
trace_all += ' SQLSMALLINT inOutType;       /* inOutType    - sql C in/out flag (in)  */' + "\n"
trace_all += ' SQLSMALLINT pfSqlCType;      /* pfSqlCType   - sql C data type   (in)  */' + "\n"
trace_all += ' SQLPOINTER  pfSqlCValue;     /* pfSqlCValue  - sql C ptr to data (out) */' + "\n"
trace_all += ' SQLINTEGER * indPtr;         /* indPtr       - sql strlen/ind    (out) */' + "\n"
trace_all += '} SQL400ParamStruct;' + "\n"
trace_all += "" + "\n"
trace_all += 'typedef struct SQL400DescStruct {' + "\n"
trace_all += ' SQLSMALLINT itype;           /*    - itype        - descr col/parm  (out) */' + "\n"
trace_all += ' SQLSMALLINT icol;            /* pc - icol         - column number   (in)  */' + "\n"
trace_all += ' SQLCHAR *   szColName;       /*  c - szColName    - column name ptr (out) */' + "\n"
trace_all += ' SQLSMALLINT cbColNameMax;    /*  c - cbColNameMax - name max len    (in)  */' + "\n"
trace_all += ' SQLSMALLINT pcbColName;      /*  c - pcbColName   - name size len   (out) */' + "\n"
trace_all += ' SQLSMALLINT pfSqlType;       /* pc - pfSqlType    - sql data type   (out) */' + "\n"
trace_all += ' SQLINTEGER  pcbColDef;       /* pc - pcbColDef    - sql size column (out) */' + "\n"
trace_all += ' SQLSMALLINT pibScale;        /* pc - pibScale     - decimal digits  (out) */' + "\n"
trace_all += ' SQLSMALLINT pfNullable;      /* pc - pfNullable   - null allowed    (out) */' + "\n"
trace_all += ' SQLCHAR     bfColName[1024]; /*  c - bfColName    - column name buf (out) */' + "\n"
trace_all += '} SQL400DescStruct;' + "\n"
trace_all += "" + "\n"
trace_all += trace_special400_main
trace_all += "" + "\n"
trace_all += "/* choose either callback or join    */" + "\n"
trace_all += "/* following structures returned     */" + "\n"
trace_all += "/* caller must free return structure */" + "\n"
trace_all += "" + "\n"
trace_all += trace_async_struct + "\n"
trace_all += "" + "\n"
trace_all += "/* join async thread                    */" + "\n"
trace_all += "/* flag:                                */" + "\n"
trace_all += "/*   SQL400_FLAG_JOIN_WAIT              */" + "\n"
trace_all += "/*     - block until complete           */" + "\n"
trace_all += "/*   SQL400_FLAG_JOIN_NO_WAIT           */" + "\n"
trace_all += "/*     - no block, NULL still executing */" + "\n"
trace_all += "" + "\n"
trace_all += trace_async_head_join
trace_all += "" + "\n"
trace_all += "" + "\n"
trace_all += "/* start an async call to DB2 CLI */" + "\n"
trace_all += "/* choose either callback or join */" + "\n"
trace_all += "/* for results returned.          */" + "\n"
trace_all += "/* sqlrc returned in structure.   */" + "\n"
trace_all += "" + "\n"
trace_all += trace_async_head_call
trace_all += "" + "\n"
trace_all += '#endif /* _PASECLIASYNC_H */' + "\n"
with open("PaseCliAsync.h", "w") as text_file:
    text_file.write(trace_all)


trace_all = ""
trace_all += "#!libdb400.a(shr.o)" + "\n"
trace_all += "" + "\n"
trace_all += "" + "\n"
trace_all += trace_override_libdb400_exp
trace_all += "" + "\n"
trace_all += "" + "\n"
with open("libdb400.exp", "w") as text_file:
    text_file.write(trace_all)



