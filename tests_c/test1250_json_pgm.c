#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdarg.h>
#include <sqlcli1.h>
#include "test.h"
#include "PaseCliAsync.h"

int main(int argc, char * argv[]) {
  SQLRETURN sqlrc = SQL_SUCCESS;
  char * injson_easy_c = "\
  {'pgm':[{'name':'RAINBOW',  'lib':'DB2JSON'},\
          {'s':[{'name':'aint8',      'type':'3i0',   'value':3},\
                {'name':'aint16',     'type':'5i0',   'value':55},\
                {'name':'aint32',     'type':'10i0',  'value':101010},\
                {'name':'aint64',     'type':'20i0',  'value':20202020},\
                {'name':'afloat',     'type':'4f2',   'value':1234.56},\
                {'name':'adouble',    'type':'8f3',   'value':123456.78},\
                {'name':'apacked',    'type':'12p2',  'value':123456.78},\
                {'name':'azoned',     'type':'12s2',  'value':123456.78},\
                {'name':'achar',      'type':'32a',   'value':'Hi there'},\
                {'name':'avarchar2',  'type':'32av2', 'value':'Hi there'},\
                {'name':'avarchar4',  'type':'32av4', 'value':'Hi there'},\
                {'name':'abinary',    'type':'3b',    'value':'313233'}\
               ]}\
         ]}";
  char injson[4096];
  int inlen = sizeof(injson);
  char outjson[4096];
  int outlen = sizeof(outjson);

  /* quote to double quote */
  test_single_double(injson_easy_c, injson, &inlen);
  printf("input(%d): %s\n",inlen,injson);

  /* json call (hdbc=0 - json handles connection) */
  sqlrc = SQL400Json(0, injson, inlen, outjson, outlen);
  printf("output(%d): %s\n",strlen(outjson),outjson);

  /* output */
  if (sqlrc == SQL_SUCCESS) {
    printf("success (%d)\n",sqlrc);
  } else {
    printf("fail (%d)\n",sqlrc);
  }

  return sqlrc;
}


