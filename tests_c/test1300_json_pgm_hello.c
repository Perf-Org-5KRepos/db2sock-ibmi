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
  {'pgm':[{'name':'HELLO',  'lib':'DB2JSON'},\
          {'s':{'name':'char', 'type':'128a', 'value':'Hi there'}}\
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

