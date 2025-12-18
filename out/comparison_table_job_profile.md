# API Comparison Table

Comparison between Legacy and Nextgen REST APIs

<style>
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }
th { background-color: #f2f2f2; }
pre { margin: 0; overflow-x: auto; }
code { display: block; white-space: pre; }
</style>

<table>
<thead>
<tr>
<th>Changed</th>
<th>Legacy Request</th>
<th>NextGen Request</th>
<th>Legacy Response</th>
<th>NextGen Response</th>
<th>Comments</th>
</tr>
</thead>
<tbody>
<tr>
<td>False</td>
<td><strong>URL:</strong> <code>/pbsworks/api/Service1/pas/restservice/profiles/profile/ShellScript/MyShellScript_V2</code><br><br><strong>Method:</strong> <code>DELETE</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;data-type&quot;: &quot;json&quot;,
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre></td>
<td><strong>URL:</strong> <code>/pbsworks/api/profiles/profile/ShellScript-2026.1.0/MyShellScript_V2?server=lenovo-01</code><br><br><strong>Method:</strong> <code>DELETE</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;data-type&quot;: &quot;json&quot;,
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre></td>
<td><strong>Status:</strong> <code>200</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre><br><br><strong>Body:</strong><br><br><pre><code class="language-json">{
  &quot;success&quot;: true,
  &quot;data&quot;: &quot;profile deleted successfully&quot;,
  &quot;exitCode&quot;: &quot;0&quot;
}</code></pre></td>
<td><strong>Status:</strong> <code>200</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre><br><br><strong>Body:</strong><br><br><pre><code class="language-json">{
  &quot;success&quot;: true,
  &quot;exitCode&quot;: &quot;0&quot;,
  &quot;data&quot;: &quot;Profile deleted successfully&quot;
}</code></pre></td>
<td>✅ No changes</td>
</tr>
<tr>
<td>True</td>
<td><strong>URL:</strong> <code>/pbsworks/api/Service1/pas/restservice/profiles</code><br><br><strong>Method:</strong> <code>GET</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;data-type&quot;: &quot;json&quot;,
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre></td>
<td><strong>URL:</strong> <code>/pbsworks/api/profiles?server=lenovo-01</code><br><br><strong>Method:</strong> <code>GET</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;data-type&quot;: &quot;json&quot;,
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre></td>
<td><strong>Status:</strong> <code>200</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre><br><br><strong>Body:</strong><br><br><pre><code class="language-json">{
  &quot;success&quot;: true,
  &quot;data&quot;: [
    {
      &quot;profileName&quot;: &quot;Last Submitted&quot;,
      &quot;profileComplete&quot;: true,
      &quot;profileData&quot;: {
        &quot;ApplicationId&quot;: &quot;ShellScript&quot;,
        &quot;ApplicationName&quot;: &quot;Shell Script&quot;,
        &quot;ApplicationFileExtension&quot;: [
          &quot;&quot;
        ],
        &quot;Tags&quot;: [
          &quot;&quot;
        ],
        &quot;NCPUS&quot;: 1,
        &quot;QUEUE&quot;: &quot;workq&quot;,
        &quot;CHUNKS&quot;: 1,
        &quot;CHUNK_PLACEMENT&quot;: &quot;free&quot;,
        &quot;MEMORY&quot;: 10,
        &quot;MEMORY_PLACEMENT&quot;: &quot;true&quot;,
        &quot;EXECUTION_PLATFORM&quot;: &quot;linux&quot;,
        &quot;PRIMARY_FILE&quot;: {
          &quot;value&quot;: &quot;/data/stage/fnjing/ShellScript_1765516767738/sleep60.py&quot;
        },
        &quot;FILES&quot;: [],
        &quot;SUBMISSION_DIRECTORY&quot;: {
          &quot;value&quot;: &quot;/data/stage/fnjing/ShellScript_1765516767738/sleep60_2025_12_12_13_19_37&quot;
        },
        &quot;myapp&quot;: &quot;OtherApps&quot;,
        &quot;JOB_NAME&quot;: &quot;sleep60&quot;
      },
      &quot;created On&quot;: 1765516778000,
      &quot;last modified&quot;: 1765516778000,
      &quot;default_profile&quot;: false,
      &quot;last_submitted&quot;: true
    }
  ],
  &quot;exitCode&quot;: &quot;0&quot;
}</code></pre></td>
<td><strong>Status:</strong> <code>200</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre><br><br><strong>Body:</strong><br><br><pre><code class="language-json">{
  &quot;success&quot;: true,
  &quot;exitCode&quot;: &quot;0&quot;,
  &quot;data&quot;: [
    {
      &quot;id&quot;: &quot;profile_qwgtolihgghtciv&quot;,
      &quot;profileName&quot;: &quot;Last Submitted&quot;,
      &quot;profileComplete&quot;: true,
      &quot;profileData&quot;: {
        &quot;ApplicationId&quot;: &quot;ShellScript-2026.1.0&quot;,
        &quot;ApplicationName&quot;: &quot;Shell Script&quot;,
        &quot;CHUNKS&quot;: 1,
        &quot;CHUNK_PLACEMENT&quot;: &quot;pack&quot;,
        &quot;CORES&quot;: 1,
        &quot;EXECUTION_PLATFORM&quot;: &quot;linux&quot;,
        &quot;FILES&quot;: [],
        &quot;GPUS&quot;: 0,
        &quot;JOB_NAME&quot;: &quot;sleep60&quot;,
        &quot;MEMORY&quot;: 1,
        &quot;MEMORY_PLACEMENT&quot;: &quot;true&quot;,
        &quot;PRIMARY_FILE&quot;: {
          &quot;value&quot;: &quot;/home/fnjing/ShellScript-2026.1.0_1765530537967/sleep60.py&quot;
        },
        &quot;QUEUE&quot;: &quot;workq&quot;,
        &quot;SUBMISSION_DIRECTORY&quot;: {
          &quot;value&quot;: &quot;/home/fnjing/ShellScript-2026.1.0_1765530537967/sleep60_2025_12_12_17_09_13&quot;
        },
        &quot;Tags&quot;: [
          &quot;Platform:Linux, Windows&quot;,
          &quot;Application Type:Batch&quot;
        ],
        &quot;myapp&quot;: &quot;OtherApps&quot;
      },
      &quot;defaultView&quot;: false,
      &quot;created On&quot;: 1765248606889,
      &quot;last modified&quot;: 1765530553954,
      &quot;default_profile&quot;: false,
      &quot;last_submitted&quot;: true,
      &quot;serverId&quot;: &quot;lenovo-01&quot;,
      &quot;applicationId&quot;: &quot;ShellScript-2026.1.0&quot;,
      &quot;userName&quot;: &quot;fnjing&quot;,
      &quot;profile_type&quot;: &quot;global&quot;
    }
  ]
}</code></pre></td>
<td>- <strong>Response Body:</strong><br>  - <strong>Added</strong> at <code>data[*].serverId</code>:<br>  <code>str</code><br>  - <strong>Added</strong> at <code>data[*].profile_type</code>:<br>  <code>str</code><br>  - <strong>Added</strong> at <code>data[*].defaultView</code>:<br>  <code>bool</code><br>  - <strong>Added</strong> at <code>data[*].id</code>:<br>  <code>str</code><br>  - <strong>Removed</strong> at <code>data[*].profileData.ApplicationFileExtension</code>:<br><pre><code class="language-json">  [
    &quot;str&quot;
  ]</code></pre><br>  - <strong>Added</strong> at <code>data[*].profileData.CORES</code>:<br>  <code>int</code><br>  - <strong>Added</strong> at <code>data[*].profileData.GPUS</code>:<br>  <code>int</code><br>  - <strong>Removed</strong> at <code>data[*].profileData.NCPUS</code>:<br>  <code>int</code><br>  - <strong>Added</strong> at <code>data[*].applicationId</code>:<br>  <code>str</code><br>  - <strong>Added</strong> at <code>data[*].userName</code>:<br>  <code>str</code></td>
</tr>
<tr>
<td>False</td>
<td><strong>URL:</strong> <code>/pbsworks/api/Service1/pas/restservice/profiles?scope=user</code><br><br><strong>Method:</strong> <code>GET</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;data-type&quot;: &quot;json&quot;,
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre></td>
<td><strong>URL:</strong> <code>/pbsworks/api/profiles?scope=user&amp;server=lenovo-01</code><br><br><strong>Method:</strong> <code>GET</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;data-type&quot;: &quot;json&quot;,
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre></td>
<td><strong>Status:</strong> <code>200</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre><br><br><strong>Body:</strong><br><br><pre><code class="language-json">{
  &quot;success&quot;: true,
  &quot;data&quot;: [],
  &quot;exitCode&quot;: &quot;0&quot;
}</code></pre></td>
<td><strong>Status:</strong> <code>200</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre><br><br><strong>Body:</strong><br><br><pre><code class="language-json">{
  &quot;success&quot;: true,
  &quot;exitCode&quot;: &quot;0&quot;,
  &quot;data&quot;: []
}</code></pre></td>
<td>✅ No changes</td>
</tr>
<tr>
<td>True</td>
<td><strong>URL:</strong> <code>/pbsworks/api/Service1/pas/restservice/profiles/profile/renamewithupdate/ShellScript/MyShellScript_V1/MyShellScript_V2?isDefault=false</code><br><br><strong>Method:</strong> <code>POST</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;data-type&quot;: &quot;json&quot;,
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre><br><br><strong>Body:</strong><br><br><pre><code class="language-json">{
  &quot;profileName&quot;: &quot;MyShellScript_V2&quot;,
  &quot;profileComplete&quot;: true,
  &quot;profileData&quot;: {
    &quot;ApplicationId&quot;: &quot;ShellScript&quot;,
    &quot;NCPUS&quot;: 1,
    &quot;QUEUE&quot;: &quot;workq&quot;,
    &quot;CHUNKS&quot;: 1,
    &quot;CHUNK_PLACEMENT&quot;: &quot;free&quot;,
    &quot;MEMORY&quot;: 22,
    &quot;MEMORY_PLACEMENT&quot;: &quot;true&quot;,
    &quot;EXECUTION_PLATFORM&quot;: &quot;linux&quot;,
    &quot;PRIMARY_FILE&quot;: {
      &quot;value&quot;: &quot;&quot;
    },
    &quot;FILES&quot;: [],
    &quot;SUBMISSION_DIRECTORY&quot;: {
      &quot;value&quot;: &quot;&quot;
    }
  },
  &quot;defaultView&quot;: false
}</code></pre></td>
<td><strong>URL:</strong> <code>/pbsworks/api/profiles/profile/renamewithupdate/ShellScript-2026.1.0/MyShellScript/MyShellScript_V2?isDefault=false&amp;server=lenovo-01</code><br><br><strong>Method:</strong> <code>POST</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;data-type&quot;: &quot;json&quot;,
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre><br><br><strong>Body:</strong><br><br><pre><code class="language-json">{
  &quot;profileName&quot;: &quot;MyShellScript_V2&quot;,
  &quot;profileComplete&quot;: true,
  &quot;profileData&quot;: {
    &quot;ApplicationId&quot;: &quot;ShellScript-2026.1.0&quot;,
    &quot;ApplicationName&quot;: &quot;Shell Script&quot;,
    &quot;QUEUE&quot;: &quot;workq&quot;,
    &quot;CORES&quot;: 1,
    &quot;MEMORY&quot;: 1,
    &quot;EXECUTION_PLATFORM&quot;: &quot;linux&quot;,
    &quot;SUBMISSION_DIRECTORY&quot;: {
      &quot;value&quot;: &quot;&quot;
    },
    &quot;PRIMARY_FILE&quot;: {
      &quot;value&quot;: &quot;/home/pbsworks/ShellScript-2026.1.0_1766035890935/sleep60.py&quot;
    },
    &quot;FILES&quot;: [],
    &quot;CHUNKS&quot;: 1,
    &quot;CHUNK_PLACEMENT&quot;: &quot;pack&quot;,
    &quot;MEMORY_PLACEMENT&quot;: &quot;true&quot;
  },
  &quot;defaultView&quot;: false
}</code></pre></td>
<td><strong>Status:</strong> <code>201</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre><br><br><strong>Body:</strong><br><br><pre><code class="language-json">{
  &quot;success&quot;: true,
  &quot;data&quot;: {
    &quot;profileName&quot;: &quot;MyShellScript_V2&quot;,
    &quot;profileComplete&quot;: true,
    &quot;profileData&quot;: {
      &quot;ApplicationId&quot;: &quot;ShellScript&quot;,
      &quot;NCPUS&quot;: 1,
      &quot;QUEUE&quot;: &quot;workq&quot;,
      &quot;CHUNKS&quot;: 1,
      &quot;CHUNK_PLACEMENT&quot;: &quot;free&quot;,
      &quot;MEMORY&quot;: 22,
      &quot;MEMORY_PLACEMENT&quot;: &quot;true&quot;,
      &quot;EXECUTION_PLATFORM&quot;: &quot;linux&quot;,
      &quot;PRIMARY_FILE&quot;: {
        &quot;value&quot;: &quot;&quot;
      },
      &quot;FILES&quot;: [],
      &quot;SUBMISSION_DIRECTORY&quot;: {
        &quot;value&quot;: &quot;&quot;
      }
    },
    &quot;defaultView&quot;: false,
    &quot;created On&quot;: 1765961324000,
    &quot;last modified&quot;: 1765961324000,
    &quot;default_profile&quot;: false,
    &quot;last_submitted&quot;: false
  },
  &quot;exitCode&quot;: &quot;0&quot;
}</code></pre></td>
<td><strong>Status:</strong> <code>200</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre><br><br><strong>Body:</strong><br><br><pre><code class="language-json">{
  &quot;success&quot;: true,
  &quot;exitCode&quot;: &quot;0&quot;,
  &quot;data&quot;: {
    &quot;id&quot;: &quot;profile_tawaxmzzgmehijj&quot;,
    &quot;profileName&quot;: &quot;MyShellScript_V2&quot;,
    &quot;profileComplete&quot;: true,
    &quot;profileData&quot;: {
      &quot;ApplicationId&quot;: &quot;ShellScript-2026.1.0&quot;,
      &quot;ApplicationName&quot;: &quot;Shell Script&quot;,
      &quot;CHUNKS&quot;: 1,
      &quot;CHUNK_PLACEMENT&quot;: &quot;pack&quot;,
      &quot;CORES&quot;: 1,
      &quot;EXECUTION_PLATFORM&quot;: &quot;linux&quot;,
      &quot;FILES&quot;: [],
      &quot;MEMORY&quot;: 1,
      &quot;MEMORY_PLACEMENT&quot;: &quot;true&quot;,
      &quot;PRIMARY_FILE&quot;: {
        &quot;value&quot;: &quot;/home/pbsworks/ShellScript-2026.1.0_1766035890935/sleep60.py&quot;
      },
      &quot;QUEUE&quot;: &quot;workq&quot;,
      &quot;SUBMISSION_DIRECTORY&quot;: {
        &quot;value&quot;: &quot;&quot;
      }
    },
    &quot;defaultView&quot;: false,
    &quot;created On&quot;: 1766035927933,
    &quot;last modified&quot;: 1766035988636,
    &quot;default_profile&quot;: false,
    &quot;last_submitted&quot;: false,
    &quot;serverId&quot;: &quot;lenovo-01&quot;,
    &quot;applicationId&quot;: &quot;ShellScript-2026.1.0&quot;,
    &quot;userName&quot;: &quot;pbsworks&quot;,
    &quot;profile_type&quot;: &quot;global&quot;
  }
}</code></pre></td>
<td>- <strong>Request Body:</strong><br>  - <strong>Added</strong> at <code>profileData.ApplicationName</code>:<br>  <code>Shell Script</code><br>  - <strong>Added</strong> at <code>profileData.CORES</code>:<br>  <code>1</code><br>  - <strong>Removed</strong> at <code>profileData.NCPUS</code>:<br>  <code>1</code><br>- <strong>Response Status:</strong> Legacy <code>201</code> → Nextgen <code>200</code><br>- <strong>Response Body:</strong><br>  - <strong>Added</strong> at <code>data.serverId</code>:<br>  <code>lenovo-01</code><br>  - <strong>Added</strong> at <code>data.profile_type</code>:<br>  <code>global</code><br>  - <strong>Added</strong> at <code>data.id</code>:<br>  <code>profile_tawaxmzzgmehijj</code><br>  - <strong>Added</strong> at <code>data.profileData.ApplicationName</code>:<br>  <code>Shell Script</code><br>  - <strong>Added</strong> at <code>data.profileData.CORES</code>:<br>  <code>1</code><br>  - <strong>Removed</strong> at <code>data.profileData.NCPUS</code>:<br>  <code>1</code><br>  - <strong>Added</strong> at <code>data.applicationId</code>:<br>  <code>ShellScript-2026.1.0</code><br>  - <strong>Added</strong> at <code>data.userName</code>:<br>  <code>pbsworks</code></td>
</tr>
<tr>
<td>True</td>
<td><strong>URL:</strong> <code>/pbsworks/api/Service1/pas/restservice/profiles/profile/renamewithupdate/ShellScript/MyShellScript/MyShellScript?isDefault=false</code><br><br><strong>Method:</strong> <code>POST</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;data-type&quot;: &quot;json&quot;,
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre><br><br><strong>Body:</strong><br><br><pre><code class="language-json">{
  &quot;profileName&quot;: &quot;MyShellScript&quot;,
  &quot;profileComplete&quot;: true,
  &quot;profileData&quot;: {
    &quot;ApplicationId&quot;: &quot;ShellScript&quot;,
    &quot;NCPUS&quot;: 1,
    &quot;QUEUE&quot;: &quot;workq&quot;,
    &quot;CHUNKS&quot;: 1,
    &quot;CHUNK_PLACEMENT&quot;: &quot;free&quot;,
    &quot;MEMORY&quot;: 22,
    &quot;MEMORY_PLACEMENT&quot;: &quot;true&quot;,
    &quot;EXECUTION_PLATFORM&quot;: &quot;linux&quot;,
    &quot;PRIMARY_FILE&quot;: {
      &quot;value&quot;: &quot;&quot;
    },
    &quot;FILES&quot;: [],
    &quot;SUBMISSION_DIRECTORY&quot;: {
      &quot;value&quot;: &quot;&quot;
    }
  },
  &quot;defaultView&quot;: false
}</code></pre></td>
<td><strong>URL:</strong> <code>/pbsworks/api/profiles/profile/save?isDefault=true&amp;server=lenovo-01</code><br><br><strong>Method:</strong> <code>POST</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;data-type&quot;: &quot;json&quot;,
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre><br><br><strong>Body:</strong><br><br><pre><code class="language-json">{
  &quot;profileName&quot;: &quot;MyShellScript_V1&quot;,
  &quot;profileComplete&quot;: true,
  &quot;profileData&quot;: {
    &quot;ApplicationId&quot;: &quot;ShellScript-2026.1.0&quot;,
    &quot;ApplicationName&quot;: &quot;Shell Script&quot;,
    &quot;QUEUE&quot;: &quot;workq&quot;,
    &quot;CORES&quot;: 1,
    &quot;MEMORY&quot;: 1,
    &quot;EXECUTION_PLATFORM&quot;: &quot;linux&quot;,
    &quot;SUBMISSION_DIRECTORY&quot;: {
      &quot;value&quot;: &quot;&quot;
    },
    &quot;PRIMARY_FILE&quot;: {
      &quot;value&quot;: &quot;/home/pbsworks/ShellScript-2026.1.0_1766035890935/sleep60.py&quot;
    },
    &quot;FILES&quot;: [],
    &quot;CHUNKS&quot;: 1,
    &quot;CHUNK_PLACEMENT&quot;: &quot;pack&quot;,
    &quot;MEMORY_PLACEMENT&quot;: &quot;true&quot;
  },
  &quot;defaultView&quot;: false
}</code></pre></td>
<td><strong>Status:</strong> <code>201</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre><br><br><strong>Body:</strong><br><br><pre><code class="language-json">{
  &quot;success&quot;: true,
  &quot;data&quot;: {
    &quot;profileName&quot;: &quot;MyShellScript&quot;,
    &quot;profileComplete&quot;: true,
    &quot;profileData&quot;: {
      &quot;ApplicationId&quot;: &quot;ShellScript&quot;,
      &quot;NCPUS&quot;: 1,
      &quot;QUEUE&quot;: &quot;workq&quot;,
      &quot;CHUNKS&quot;: 1,
      &quot;CHUNK_PLACEMENT&quot;: &quot;free&quot;,
      &quot;MEMORY&quot;: 22,
      &quot;MEMORY_PLACEMENT&quot;: &quot;true&quot;,
      &quot;EXECUTION_PLATFORM&quot;: &quot;linux&quot;,
      &quot;PRIMARY_FILE&quot;: {
        &quot;value&quot;: &quot;&quot;
      },
      &quot;FILES&quot;: [],
      &quot;SUBMISSION_DIRECTORY&quot;: {
        &quot;value&quot;: &quot;&quot;
      }
    },
    &quot;defaultView&quot;: false,
    &quot;created On&quot;: 1765961304000,
    &quot;last modified&quot;: 1765961304000,
    &quot;default_profile&quot;: false,
    &quot;last_submitted&quot;: false
  },
  &quot;exitCode&quot;: &quot;0&quot;
}</code></pre></td>
<td><strong>Status:</strong> <code>200</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre><br><br><strong>Body:</strong><br><br><pre><code class="language-json">{
  &quot;success&quot;: true,
  &quot;exitCode&quot;: &quot;0&quot;,
  &quot;data&quot;: {
    &quot;id&quot;: &quot;profile_tjpmrzmitgvhhvm&quot;,
    &quot;profileName&quot;: &quot;MyShellScript_V1&quot;,
    &quot;profileComplete&quot;: true,
    &quot;profileData&quot;: {
      &quot;ApplicationId&quot;: &quot;ShellScript-2026.1.0&quot;,
      &quot;ApplicationName&quot;: &quot;Shell Script&quot;,
      &quot;CHUNKS&quot;: 1,
      &quot;CHUNK_PLACEMENT&quot;: &quot;pack&quot;,
      &quot;CORES&quot;: 1,
      &quot;EXECUTION_PLATFORM&quot;: &quot;linux&quot;,
      &quot;FILES&quot;: [],
      &quot;MEMORY&quot;: 1,
      &quot;MEMORY_PLACEMENT&quot;: &quot;true&quot;,
      &quot;PRIMARY_FILE&quot;: {
        &quot;value&quot;: &quot;/home/pbsworks/ShellScript-2026.1.0_1766035890935/sleep60.py&quot;
      },
      &quot;QUEUE&quot;: &quot;workq&quot;,
      &quot;SUBMISSION_DIRECTORY&quot;: {
        &quot;value&quot;: &quot;&quot;
      }
    },
    &quot;defaultView&quot;: false,
    &quot;created On&quot;: 1766035957159,
    &quot;last modified&quot;: 1766035957159,
    &quot;default_profile&quot;: true,
    &quot;last_submitted&quot;: false,
    &quot;serverId&quot;: &quot;lenovo-01&quot;,
    &quot;applicationId&quot;: &quot;ShellScript-2026.1.0&quot;,
    &quot;userName&quot;: &quot;pbsworks&quot;,
    &quot;profile_type&quot;: &quot;global&quot;
  }
}</code></pre></td>
<td>- <strong>Request Body:</strong><br>  - <strong>Added</strong> at <code>profileData.ApplicationName</code>:<br>  <code>Shell Script</code><br>  - <strong>Added</strong> at <code>profileData.CORES</code>:<br>  <code>1</code><br>  - <strong>Removed</strong> at <code>profileData.NCPUS</code>:<br>  <code>1</code><br>- <strong>Response Status:</strong> Legacy <code>201</code> → Nextgen <code>200</code><br>- <strong>Response Body:</strong><br>  - <strong>Added</strong> at <code>data.serverId</code>:<br>  <code>lenovo-01</code><br>  - <strong>Added</strong> at <code>data.profile_type</code>:<br>  <code>global</code><br>  - <strong>Added</strong> at <code>data.id</code>:<br>  <code>profile_tjpmrzmitgvhhvm</code><br>  - <strong>Added</strong> at <code>data.profileData.ApplicationName</code>:<br>  <code>Shell Script</code><br>  - <strong>Added</strong> at <code>data.profileData.CORES</code>:<br>  <code>1</code><br>  - <strong>Removed</strong> at <code>data.profileData.NCPUS</code>:<br>  <code>1</code><br>  - <strong>Added</strong> at <code>data.applicationId</code>:<br>  <code>ShellScript-2026.1.0</code><br>  - <strong>Added</strong> at <code>data.userName</code>:<br>  <code>pbsworks</code></td>
</tr>
<tr>
<td>True</td>
<td><strong>URL:</strong> <code>/pbsworks/api/Service1/pas/restservice/profiles/profile/renamewithupdate/ShellScript/MyShellScript/MyShellScript?isDefault=true</code><br><br><strong>Method:</strong> <code>POST</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;data-type&quot;: &quot;json&quot;,
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre></td>
<td><strong>URL:</strong> <code>/pbsworks/api/profiles/profile/default/ShellScript-2026.1.0/MyShellScript_V2?server=lenovo-01</code><br><br><strong>Method:</strong> <code>POST</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;data-type&quot;: &quot;json&quot;,
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre></td>
<td><strong>Status:</strong> <code>201</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre><br><br><strong>Body:</strong><br><br><pre><code class="language-json">{
  &quot;success&quot;: true,
  &quot;data&quot;: {
    &quot;profileName&quot;: &quot;MyShellScript&quot;,
    &quot;profileComplete&quot;: true,
    &quot;profileData&quot;: {
      &quot;ApplicationId&quot;: &quot;ShellScript&quot;,
      &quot;NCPUS&quot;: 1,
      &quot;QUEUE&quot;: &quot;workq&quot;,
      &quot;CHUNKS&quot;: 1,
      &quot;CHUNK_PLACEMENT&quot;: &quot;free&quot;,
      &quot;MEMORY&quot;: 22,
      &quot;MEMORY_PLACEMENT&quot;: &quot;true&quot;,
      &quot;EXECUTION_PLATFORM&quot;: &quot;linux&quot;,
      &quot;PRIMARY_FILE&quot;: {
        &quot;value&quot;: &quot;&quot;
      },
      &quot;FILES&quot;: [],
      &quot;SUBMISSION_DIRECTORY&quot;: {
        &quot;value&quot;: &quot;&quot;
      }
    },
    &quot;defaultView&quot;: false,
    &quot;created On&quot;: 1765961313000,
    &quot;last modified&quot;: 1765961313000,
    &quot;default_profile&quot;: true,
    &quot;last_submitted&quot;: false
  },
  &quot;exitCode&quot;: &quot;0&quot;
}</code></pre></td>
<td><strong>Status:</strong> <code>200</code><br><br><strong>Headers:</strong><br><br><pre><code class="language-json">{
  &quot;content-type&quot;: &quot;application/json&quot;
}</code></pre><br><br><strong>Body:</strong><br><br><pre><code class="language-json">{
  &quot;success&quot;: true,
  &quot;exitCode&quot;: &quot;0&quot;,
  &quot;data&quot;: &quot;Default profile set successfully&quot;
}</code></pre></td>
<td>- <strong>Response Status:</strong> Legacy <code>201</code> → Nextgen <code>200</code><br>- <strong>Response Body:</strong><br>  - <strong>Type mismatch</strong> at <code>data</code>:<br>    - Legacy type: <code>dict</code><br>    - Nextgen type: <code>str</code></td>
</tr>
</tbody>
</table>