# API Comparison Report

Comparison between Legacy and Nextgen REST APIs

## Summary

- **Total Legacy APIs**: 32
- **Total Nextgen APIs**: 32
- **Common APIs**: 27
- **Legacy Only**: 5
- **Nextgen Only**: 5

## Common Endpoints Comparison

### GET /pbsworks/api/Service1/pas/restservice/applications

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/applications`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/applications?server=lenovo-01`

#### Request Comparison

✅ Request structure is identical

#### Response Comparison

✅ Response structure is identical

---

### GET /pbsworks/api/Service1/pas/restservice/applications/actions

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/applications/actions`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/applications/actions?server=lenovo-01`

#### Request Comparison

✅ Request structure is identical

#### Response Comparison

✅ Response structure is identical

---

### GET /pbsworks/api/Service1/pas/restservice/applications/ids

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/applications/ids?privileged=false`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/applications/ids?privileged=false&server=lenovo-01`

#### Request Comparison

✅ Request structure is identical

#### Response Comparison

✅ Response structure is identical

---

### GET /pbsworks/api/Service1/pas/restservice/server/qmgr

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/server/qmgr`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/server/qmgr?server=lenovo-01`

#### Request Comparison

✅ Request structure is identical

#### Response Comparison

✅ Response structure is identical

---

### GET /pbsworks/api/Service1/pas/restservice/server/queues

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/server/queues`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/server/queues?server=lenovo-01`

#### Request Comparison

✅ Request structure is identical

#### Response Comparison

✅ Response structure is identical

---

### GET /pbsworks/api/Service1/pas/restservice/server/version

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/server/version`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/server/version`

#### Request Comparison

✅ Request structure is identical

#### Response Comparison

✅ Response structure is identical

---

### GET /pbsworks/api/access/info

- **Legacy URL**: `/pbsworks/api/access/info`
- **Nextgen URL**: `/pbsworks/api/access/info`

#### Request Comparison

✅ Request structure is identical

#### Response Comparison

✅ Response structure is identical

---

### GET /pbsworks/api/ams/aaservice/authn/oauth2/validatetoken

- **Legacy URL**: `/pbsworks/api/ams/aaservice/authn/oauth2/validatetoken`
- **Nextgen URL**: `/pbsworks/api/ams/aaservice/authn/oauth2/validatetoken`

#### Request Comparison

✅ Request structure is identical

#### Response Comparison

✅ Response structure is identical

---

### GET /pbsworks/api/resultmanagerservice/rest/rmservice/allServersFilePatternsNew

- **Legacy URL**: `/pbsworks/api/resultmanagerservice/rest/rmservice/allServersFilePatternsNew`
- **Nextgen URL**: `/pbsworks/api/resultmanagerservice/rest/rmservice/allServersFilePatternsNew`

#### Request Comparison

✅ Request structure is identical

#### Response Comparison

✅ Response structure is identical

---

### GET /pbsworks/api/resultmanagerservice/rest/rmservice/getHWConfigDetails

- **Legacy URL**: `/pbsworks/api/resultmanagerservice/rest/rmservice/getHWConfigDetails`
- **Nextgen URL**: `/pbsworks/api/resultmanagerservice/rest/rmservice/getHWConfigDetails`

#### Request Comparison

✅ Request structure is identical

#### Response Comparison

✅ Response structure is identical

---

### GET /pbsworks/api/storage/service

- **Legacy URL**: `/pbsworks/api/storage/service`
- **Nextgen URL**: `/pbsworks/api/storage/service`

#### Request Comparison

✅ Request structure is identical

#### Response Comparison

**Headers:**
**Modified headers:**
- `content-type`:
  - Legacy: `application/hal+json`
  - Nextgen: `application/json`

---

### GET /pbsworks/api/storage/userdata

- **Legacy URL**: `/pbsworks/api/storage/userdata`
- **Nextgen URL**: `/pbsworks/api/storage/userdata`

#### Request Comparison

✅ Request structure is identical

#### Response Comparison

✅ Response structure is identical

---

### POST /pbsworks/api/Service1/pas/restservice/files/bulkdelete

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/files/bulkdelete`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/files/bulkdelete`

#### Request Comparison

**Body Differences:**
- **Modified** at `paths[0]`:
  - Legacy: `/data/stage/fnjing/new name`
  - Nextgen: `/home/fnjing/My Folder`

#### Response Comparison

✅ Response structure is identical

---

### POST /pbsworks/api/Service1/pas/restservice/files/changepermission

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/files/changepermission`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/files/changepermission`

#### Request Comparison

**Body Differences:**
- **Modified** at `paths[0]`:
  - Legacy: `/data/stage/fnjing/new name`
  - Nextgen: `/home/fnjing/ShellScript-2026.1_archive_1765510611961.zip`

#### Response Comparison

✅ Response structure is identical

---

### POST /pbsworks/api/Service1/pas/restservice/files/compress

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/files/compress`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/files/compress`

#### Request Comparison

**Body Differences:**
- **Modified** at `file`:
  - Legacy: `/data/stage/fnjing/new name_archive_1765516620836.zip`
  - Nextgen: `/home/fnjing/New Text Document_archive_1765510605672.zip`
- **Modified** at `paths[0]`:
  - Legacy: `/data/stage/fnjing/new name`
  - Nextgen: `/home/fnjing/New Text Document.txt`

#### Response Comparison

- **Status Code**: Legacy `200` → Nextgen `409`

---

### POST /pbsworks/api/Service1/pas/restservice/files/dir/create

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/files/dir/create`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/files/dir/create`

#### Request Comparison

**Body Differences:**
- **Modified** at `path`:
  - Legacy: `/data/stage/fnjing/My Folder`
  - Nextgen: `/home/fnjing/My Folder`
- **Added** at `jobid`: `null`

#### Response Comparison

- **Status Code**: Legacy `201` → Nextgen `200`

---

### POST /pbsworks/api/Service1/pas/restservice/files/expandvars

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/files/expandvars`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/files/expandvars`

#### Request Comparison

**Body Differences:**
- **Modified** at `paths[0]`:
  - Legacy: `/data/share`
  - Nextgen: `$HOME`
- **Removed** at `paths[1]`: `/data/home/$USER`
- **Removed** at `paths[2]`: `/data/stage/$USER`

#### Response Comparison

✅ Response structure is identical

---

### POST /pbsworks/api/Service1/pas/restservice/files/file/dataReplace

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/files/file/dataReplace`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/files/file/dataReplace`

#### Request Comparison

**Body Differences:**
- **Modified** at `replacementType[0].data`:
  - Legacy: `ZWRpdCBpdA==`
  - Nextgen: `dGVzdCBlZGl0`
- **Type mismatch** at `replacementType[0].oldBytesCount`:
  - Legacy type: `int`
  - Nextgen type: `NoneType`
- **Modified** at `fileName`:
  - Legacy: `/data/stage/fnjing/New Text Document.txt`
  - Nextgen: `/home/fnjing/New Text Document.txt`

#### Response Comparison

✅ Response structure is identical

---

### POST /pbsworks/api/Service1/pas/restservice/files/file/exists

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/files/file/exists`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/files/file/exists`

#### Request Comparison

**Body Differences:**
- **Modified** at `paths[0]`:
  - Legacy: `/data/stage/fnjing`
  - Nextgen: `/home/fnjing`

#### Response Comparison

✅ Response structure is identical

---

### POST /pbsworks/api/Service1/pas/restservice/files/file/move

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/files/file/move`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/files/file/move`

#### Request Comparison

**Body Differences:**
- **Modified** at `destination`:
  - Legacy: `/data/stage/fnjing/New folder`
  - Nextgen: `/home/fnjing/ShellScript-2026.1_archive_1765510611961.zip`
- **Modified** at `source[0]`:
  - Legacy: `/data/stage/fnjing/New Text Document - Copy.txt`
  - Nextgen: `/home/fnjing/ShellScript-2026.1_archive_1765510611960.zip`

#### Response Comparison

✅ Response structure is identical

---

### POST /pbsworks/api/Service1/pas/restservice/files/file/read

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/files/file/read`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/files/file/read`

#### Request Comparison

**Body Differences:**
- **Modified** at `path`:
  - Legacy: `/data/stage/fnjing/sleep60.py`
  - Nextgen: `/home/fnjing/ShellScript-2026.1.0_1765444350173/sleep60_2025_12_11_17_13_05/sleep60.o1008`
- **Modified** at `size`:
  - Legacy: `0`
  - Nextgen: `25000`

#### Response Comparison

✅ Response structure is identical

---

### POST /pbsworks/api/Service1/pas/restservice/files/file/uncompress

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/files/file/uncompress`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/files/file/uncompress`

#### Request Comparison

**Body Differences:**
- **Modified** at `file`:
  - Legacy: `/data/stage/fnjing/new name_archive_1765516620836.zip`
  - Nextgen: `/home/fnjing/ShellScript-2026.1_archive_1765510611961.zip`
- **Modified** at `path`:
  - Legacy: `/data/stage/fnjing`
  - Nextgen: `/home/fnjing`

#### Response Comparison

✅ Response structure is identical

---

### POST /pbsworks/api/Service1/pas/restservice/files/file/write

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/files/file/write`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/files/file/write`

#### Request Comparison

**Body Differences:**
- **Added** at `jobid`: `null`
- **Modified** at `path`:
  - Legacy: `/data/stage/fnjing/New Text Document.txt`
  - Nextgen: `/home/fnjing/New Text Document.txt`

#### Response Comparison

- **Status Code**: Legacy `201` → Nextgen `200`

---

### POST /pbsworks/api/Service1/pas/restservice/files/list

- **Legacy URL**: `/pbsworks/api/Service1/pas/restservice/files/list?page=1&size=50&jobstatus=undefined&sortby=name&sortorder=ASC`
- **Nextgen URL**: `/pbsworks/api/Service1/pas/restservice/files/list`

#### Request Comparison

**Body Differences:**
- **Modified** at `path`:
  - Legacy: `/data/stage/fnjing`
  - Nextgen: `/home/fnjing/ShellScript-2026.1.0_1765444350173/sleep60_2025_12_11_17_13_05`
- **Removed** at `chroots`: `null`

#### Response Comparison

✅ Response structure is identical

---

### POST /pbsworks/api/preferences/userpreferences

- **Legacy URL**: `/pbsworks/api/preferences/userpreferences`
- **Nextgen URL**: `/pbsworks/api/preferences/userpreferences`

#### Request Comparison

✅ Request structure is identical

#### Response Comparison

✅ Response structure is identical

---

### POST /pbsworks/api/storage/jobs/query

- **Legacy URL**: `/pbsworks/api/storage/jobs/query`
- **Nextgen URL**: `/pbsworks/api/storage/jobs/query`

#### Request Comparison

**Body Differences:**
- **Type mismatch** at `where[1].value[0]`:
  - Legacy type: `str`
  - Nextgen type: `int`
- **Modified** at `columns[9]`:
  - Legacy: `pbsserver.id`
  - Nextgen: `pbsserverId`
- **Added** at `columns[22]`: `progress`

#### Response Comparison

✅ Response structure is identical

---

### POST /pbsworks/api/storage/userdata

- **Legacy URL**: `/pbsworks/api/storage/userdata`
- **Nextgen URL**: `/pbsworks/api/storage/userdata`

#### Request Comparison

**Body Differences:**
- **Added** at `[1].data.array`: ```json
{
  "Array Jobs": true,
  "Batch Jobs": true
}
```
- **Removed** at `[1].data.fileRoutingProps`: ```json
{
  "params": {
    "serverName": "hpccluster",
    "selectedPath": "/data/stage/fnjing",
    "page": 1,
    "sortby": "name",
    "sortorder": "ASC",
    "fileViewType": "listview"
  },
  "location": "https://192.168.40.61/pbsworks/jobs?serverName=hpccluster&selectedPath=%2Fdata%2Fstage%2Ffnjing&page=1&sortby=name&sortorder=ASC",
  "query": "?serverName=hpccluster&selectedPath=%2Fdata%2Fstage%2Ffnjing&page=1&sortby=name&sortorder=ASC"
}
```
- **Added** at `[1].data.userFilter`: `My Jobs`
- **Added** at `[1].data.timeFilter`: `Last 7 days`
- **Added** at `[1].data.access_token`: ```json
{
  "eyJhbGciOiJSUzI1NiIsImtpZCI6IjJiZTQxOWM0M2E2NDUzNTVkNmU3ODdiZjBhNWNkODNiYTgzYjI1ZDgifQ.eyJpc3MiOiJodHRwczovLzE5Mi4xNjguMTAwLjE5NDo0NDQzL3Bic3dvcmtzL29pZGMiLCJzdWIiOiJmbmppbmciLCJhdWQiOiJhY2Nlc3Mtd2ViIiwiZXhwIjoxNzY1NjE3NzUyLCJpYXQiOjE3NjU1MDk3NTIsImF0X2hhc2giOiJCOWZtQnpPd0NmNTdsV1NlZDNEdVpnIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJuYW1lIjoiZm5qaW5nIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiZm5qaW5nIn0.BvVLDveCkGx_gD1GZqAQgRaSFrr688VFgFUT-5sADBlOsxyWbg2BQizbN5VASaocdNenX7emIURqZzEuug3LZZNK5MCfR3lKlErEbvIE0-CcSGldk0rO6LNUi4k131s6NBUmFt_q6Kghse1CNHjdF4-MZje84HOHWUI-Vi-H-0FYnm3byWp54Hxx95B4XFyS3TBdXGrTM6BaVAWwB-IvaeHWnOwjCk7O9R7C6j6pkOig0r-KU_a1Bwj1Wzy14PgWaFVzsokTViL6_Ma0ClnP-awkuqTcvDWVFtYYZeIOB0MTaVvNztmw7II_x77oYViXRopZAXOowiAOJMVM1G4SRA": true
}
```
- **Modified** at `[1].name`:
  - Legacy: `FILES_ROUTE`
  - Nextgen: `SELECTED_JOB_FILTERS`
- **Added** at `[2]`: ```json
{
  "name": "FILES_ROUTE",
  "userName": "fnjing",
  "data": {
    "fileRoutingProps": {
      "params": {
        "serverName": "lenovo-01",
        "selectedPath": "/home/fnjing",
        "page": 1,
        "sortby": "name",
        "sortorder": "ASC",
        "fileViewType": "listview"
      },
      "location": "https://access-web.wjing.xyz/pbsworks/jobs?serverName=lenovo-01&selectedPath=%2Fhome%2Ffnjing&page=1&sortby=name&sortorder=ASC",
      "query": "?serverName=lenovo-01&selectedPath=%2Fhome%2Ffnjing&page=1&sortby=name&sortorder=ASC"
    }
  }
}
```

#### Response Comparison

✅ Response structure is identical

---

## Endpoints Only in Legacy

- **GET /pbsworks/api/Service1/pas/restservice/profiles**
  - URL: `/pbsworks/api/Service1/pas/restservice/profiles`

- **GET /pbsworks/api/ams/aaservice/authz/privileges**
  - URL: `/pbsworks/api/ams/aaservice/authz/privileges?app_name=access`

- **GET /pbsworks/api/storage/jobs/189132.m1**
  - URL: `/pbsworks/api/storage/jobs/189132.m1?serverName=hpccluster`

- **POST /pbsworks/api/Service1/pas/restservice/files/file/copy**
  - URL: `/pbsworks/api/Service1/pas/restservice/files/file/copy`

- **POST /pbsworks/api/Service1/pas/restservice/jobs**
  - URL: `/pbsworks/api/Service1/pas/restservice/jobs?application_id=ShellScript&server_registered_name=hpccluster`

## Endpoints Only in Nextgen

- **GET /pbsworks/api/Service1/pas/restservice/server/nodes**
  - URL: `/pbsworks/api/Service1/pas/restservice/server/nodes?server=lenovo-01`

- **GET /pbsworks/api/policy/aaservice/authz/privileges/fnjing**
  - URL: `/pbsworks/api/policy/aaservice/authz/privileges/fnjing`

- **GET /pbsworks/api/policy/aaservice/authz/users**
  - URL: `/pbsworks/api/policy/aaservice/authz/users`

- **GET /pbsworks/api/profiles**
  - URL: `/pbsworks/api/profiles?server=lenovo-01`

- **GET /pbsworks/api/storage/jobs/1008.lenovo-01**
  - URL: `/pbsworks/api/storage/jobs/1008.lenovo-01?serverName=lenovo-01`
