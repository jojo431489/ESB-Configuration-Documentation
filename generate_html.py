# -*- coding: utf-8 -*-
import json
from collections import defaultdict
import html

# 讀取所有 JSON 檔案
all_data = {}
files = ['DataModel.json', 'ProductService.json', 'ProductServiceDetail.json']

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        all_data[f] = json.load(file)

# 收集所有資料
services = []
models = []
fields = []
db_settings = []
condition_groups = []
service_details = []

for f in files:
    data = all_data[f]

    for svc in data.get('productService', []):
        services.append({
            'file': f,
            'name': svc.get('SERVICENAME', ''),
            'desc': svc.get('SERVICEDESC', ''),
            'protocol': svc.get('SERVICEPROTOCOL', 0),
            'url': svc.get('SERVICEURL', ''),
            'enabled': svc.get('ISENABLE', 0),
            'productType': svc.get('PRODUCTTYPE', ''),
            'productCode': svc.get('PRODUCTCODE', ''),
            'retryCount': svc.get('RETRYCOUNT', 0),
            'retryCycle': svc.get('RETRYCYCLE', 0),
            'concurrence': svc.get('CONCURRENCE', 0),
            'contentFormat': svc.get('CONTENTFORMAT', 0),
            'guid': svc.get('guid', ''),
            'requestFile': svc.get('REQUESTFILE', ''),
            'responseFile': svc.get('RESPONSEFILE', ''),
            'createdate': svc.get('createdate', ''),
            'editdate': svc.get('editdate', '')
        })

    for m in data.get('dataModel', []):
        models.append({
            'file': f,
            'tableName': m.get('TABLENAME', ''),
            'modelCode': m.get('MODELCODE', ''),
            'modelName': m.get('MODELNAME', ''),
            'sqlScript': m.get('SQLSCRIPT', '') or '',
            'isView': m.get('ISVIEW', 0),
            'rowLimit': m.get('ROWLIMIT', 0),
            'guid': m.get('guid', ''),
            'createdate': m.get('createdate', ''),
            'editdate': m.get('editdate', '')
        })

    for field in data.get('dataModelField', []):
        fields.append({
            'fromGuid': field.get('FROMGUID', ''),
            'fieldName': field.get('FIELDNAME', ''),
            'dataType': field.get('DATATYPE', ''),
            'length': field.get('LENGTH', 0),
            'isKey': field.get('ISKEY', 0),
            'isNullable': field.get('ISNULLABLE', 0)
        })

    for db in data.get('dbSetting', []):
        db_settings.append({
            'file': f,
            'dbCode': db.get('DBCODE', ''),
            'dbType': db.get('DBTYPE', 0),
            'dbIP': db.get('DBIP', ''),
            'dbName': db.get('DBNAME', ''),
            'dbPort': db.get('DBPORT', '')
        })

    for cg in data.get('conditionGroup', []):
        condition_groups.append({
            'file': f,
            'modelCode': cg.get('MODELCODE', ''),
            'transferType': cg.get('TRANSFERTYPE', ''),
            'contentType': cg.get('CONTENTTYPE', '')
        })

    for sd in data.get('productServiceDetail', []):
        service_details.append({
            'fromguid': sd.get('fromguid', ''),
            'fieldname': sd.get('fieldname', ''),
            'fieldbussinessname': sd.get('fieldbussinessname', ''),
            'fieldtype': sd.get('fieldtype', ''),
            'mappingfield': sd.get('mappingfield', ''),
            'isnecessary': sd.get('isnecessary', 0),
            'iskey': sd.get('iskey', 0)
        })

# 統計服務類型
svc_by_type = defaultdict(list)
for s in services:
    svc_by_type[s['productType']].append(s)

# 統計資料模型
model_by_table = defaultdict(list)
for m in models:
    model_by_table[m['tableName']].append(m)

# 建立 model guid -> model 的對應
model_by_guid = {}
for m in models:
    model_by_guid[m['guid']] = m

# 建立欄位字典
fields_by_model = defaultdict(list)
for f in fields:
    fields_by_model[f['fromGuid']].append(f)

# 建立服務 guid -> 服務詳情
svc_detail_by_guid = defaultdict(list)
for sd in service_details:
    svc_detail_by_guid[sd['fromguid']].append(sd)

# 協議名稱對照
protocol_names = {
    0: 'HTTP',
    1: 'SOAP',
    2: 'WebService',
    3: 'REST',
    4: 'TCP',
    5: 'SAP RFC'
}

# 內容格式對照
format_names = {
    0: 'XML',
    1: 'JSON',
    2: 'Text'
}

# 開始生成 HTML
html_content = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESB 平台設定檔說明文件</title>
    <style>
        :root {
            --primary-color: #1a73e8;
            --secondary-color: #34a853;
            --warning-color: #fbbc04;
            --danger-color: #ea4335;
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
            --text-color: #202124;
            --text-secondary: #5f6368;
            --border-color: #dadce0;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', 'Microsoft JhengHei', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
        }

        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }

        header {
            background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
            color: white;
            padding: 40px 20px;
            margin-bottom: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(26,115,232,0.3);
        }

        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
        }

        header .subtitle { font-size: 1.2em; opacity: 0.9; }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .stat-icon {
            width: 60px;
            height: 60px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .stat-icon.blue { background: #e8f0fe; }
        .stat-icon.green { background: #e6f4ea; }
        .stat-icon.orange { background: #fef7e0; }
        .stat-icon.purple { background: #f3e8fd; }

        .stat-content h3 { font-size: 2em; color: var(--text-color); }
        .stat-content p { color: var(--text-secondary); font-size: 0.95em; }

        .section {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }

        .section-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--border-color);
        }

        .section-header h2 { font-size: 1.5em; color: var(--text-color); }

        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }

        .badge-primary { background: #e8f0fe; color: #1a73e8; }
        .badge-success { background: #e6f4ea; color: #137333; }
        .badge-warning { background: #fef7e0; color: #b06000; }
        .badge-danger { background: #fce8e6; color: #c5221f; }
        .badge-info { background: #f3e8fd; color: #7627bb; }

        table { width: 100%; border-collapse: collapse; margin-top: 15px; }

        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }

        th {
            background: var(--bg-color);
            font-weight: 600;
            color: var(--text-secondary);
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        tr:hover { background: #f8f9fa; }

        .service-name { font-weight: 600; color: var(--primary-color); }

        .url-cell {
            font-family: 'Consolas', monospace;
            font-size: 0.85em;
            color: var(--text-secondary);
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .code-block {
            background: #263238;
            color: #eeffff;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Consolas', monospace;
            font-size: 0.9em;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-all;
            max-height: 300px;
            overflow-y: auto;
        }

        .tabs { display: flex; gap: 5px; margin-bottom: 20px; flex-wrap: wrap; }

        .tab {
            padding: 10px 20px;
            border: none;
            background: var(--bg-color);
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.95em;
            transition: all 0.2s;
        }

        .tab:hover { background: #e8f0fe; }
        .tab.active { background: var(--primary-color); color: white; }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        .collapsible {
            background: var(--bg-color);
            border: none;
            padding: 15px 20px;
            width: 100%;
            text-align: left;
            font-size: 1em;
            cursor: pointer;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: background 0.2s;
        }

        .collapsible:hover { background: #e8f0fe; }

        .collapsible-content {
            display: none;
            padding: 20px;
            background: var(--bg-color);
            border-radius: 0 0 8px 8px;
            margin-top: -10px;
            margin-bottom: 10px;
        }

        .collapsible-content.active { display: block; }

        .arrow { transition: transform 0.2s; }
        .collapsible.active .arrow { transform: rotate(90deg); }

        .grid-2 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }

        .info-box { background: var(--bg-color); border-radius: 8px; padding: 20px; }

        .info-box h4 {
            margin-bottom: 15px;
            color: var(--text-secondary);
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .info-list { list-style: none; }

        .info-list li {
            padding: 8px 0;
            display: flex;
            justify-content: space-between;
            border-bottom: 1px dashed var(--border-color);
        }

        .info-list li:last-child { border-bottom: none; }

        .toc {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }

        .toc h3 { margin-bottom: 15px; color: var(--text-color); }

        .toc-list {
            list-style: none;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 10px;
        }

        .toc-list a {
            color: var(--primary-color);
            text-decoration: none;
            padding: 8px 15px;
            display: block;
            border-radius: 6px;
            transition: background 0.2s;
        }

        .toc-list a:hover { background: #e8f0fe; }

        footer {
            text-align: center;
            padding: 30px;
            color: var(--text-secondary);
            font-size: 0.9em;
        }

        .flow-diagram {
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
        }

        @media (max-width: 768px) {
            .stats-grid { grid-template-columns: 1fr 1fr; }
            .grid-2 { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>
                <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect width="48" height="48" rx="12" fill="white" fill-opacity="0.2"/>
                    <path d="M14 18h20v4H14v-4zm0 8h20v4H14v-4zm0-16h20v4H14v-4z" fill="white"/>
                    <circle cx="38" cy="20" r="6" fill="#34a853"/>
                    <path d="M36 20l2 2 4-4" stroke="white" stroke-width="2" fill="none"/>
                </svg>
                ESB 平台設定檔說明文件
            </h1>
            <p class="subtitle">Enterprise Service Bus Configuration Documentation - Version 1.7.0</p>
        </header>
'''

# 統計卡片
total_services = len(services)
total_models = len(models)
total_fields = len(fields)
enabled_services = sum(1 for s in services if s['enabled'] == 1)
total_details = len(service_details)

html_content += f'''
        <!-- 統計摘要 -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon blue">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                        <path d="M8 6h16v4H8V6zm0 8h16v4H8v-4zm0 8h16v4H8v-4z" fill="#1a73e8"/>
                    </svg>
                </div>
                <div class="stat-content">
                    <h3>{total_services}</h3>
                    <p>服務總數</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon green">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                        <circle cx="16" cy="16" r="10" stroke="#34a853" stroke-width="3" fill="none"/>
                        <path d="M12 16l3 3 6-6" stroke="#34a853" stroke-width="2" fill="none"/>
                    </svg>
                </div>
                <div class="stat-content">
                    <h3>{enabled_services}</h3>
                    <p>已啟用服務</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon orange">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                        <rect x="6" y="8" width="20" height="16" rx="2" stroke="#f9ab00" stroke-width="2" fill="none"/>
                        <path d="M10 14h12M10 18h8" stroke="#f9ab00" stroke-width="2"/>
                    </svg>
                </div>
                <div class="stat-content">
                    <h3>{total_models}</h3>
                    <p>資料模型</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon purple">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                        <path d="M6 10h8v4H6v-4zm0 8h8v4H6v-4zm12-8h8v4h-8v-4zm0 8h8v4h-8v-4z" fill="#7627bb"/>
                    </svg>
                </div>
                <div class="stat-content">
                    <h3>{total_fields}</h3>
                    <p>欄位定義</p>
                </div>
            </div>
        </div>
'''

# 目錄
html_content += '''
        <!-- 目錄 -->
        <div class="toc">
            <h3>📑 目錄</h3>
            <ul class="toc-list">
                <li><a href="#overview">📊 整體概覽</a></li>
                <li><a href="#architecture">🏗️ 架構說明</a></li>
                <li><a href="#file-structure">📁 檔案結構說明</a></li>
                <li><a href="#services">🔌 服務清單</a></li>
                <li><a href="#data-models">📋 資料模型</a></li>
                <li><a href="#db-settings">🗄️ 資料庫設定</a></li>
                <li><a href="#field-mapping">🔗 欄位對應說明</a></li>
            </ul>
        </div>
'''

# 整體概覽
html_content += '''
        <!-- 整體概覽 -->
        <div class="section" id="overview">
            <div class="section-header">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                    <circle cx="16" cy="16" r="14" stroke="#1a73e8" stroke-width="2" fill="none"/>
                    <path d="M16 8v8l6 4" stroke="#1a73e8" stroke-width="2" stroke-linecap="round"/>
                </svg>
                <h2>整體概覽</h2>
            </div>
            <p>本文件說明 ESB (Enterprise Service Bus) 平台的設定檔結構與內容。ESB 平台用於整合 ERP 系統與 MES 系統之間的資料交換。</p>

            <div class="grid-2" style="margin-top: 20px;">
                <div class="info-box">
                    <h4>📁 檔案清單</h4>
                    <ul class="info-list">
                        <li><span>DataModel.json</span><span class="badge badge-primary">資料模型</span></li>
                        <li><span>ProductService.json</span><span class="badge badge-success">服務定義</span></li>
                        <li><span>ProductServiceDetail.json</span><span class="badge badge-info">完整設定</span></li>
                    </ul>
                </div>
                <div class="info-box">
                    <h4>🏷️ 服務類型分布</h4>
                    <ul class="info-list">
'''

for t, svcs in sorted(svc_by_type.items()):
    badge_class = 'badge-primary' if t == 'MES' else 'badge-success' if t == 'WFGP' else 'badge-warning'
    html_content += f'                        <li><span>{html.escape(t)}</span><span class="badge {badge_class}">{len(svcs)} 個服務</span></li>\n'

html_content += '''
                    </ul>
                </div>
            </div>
        </div>
'''

# 架構說明
html_content += '''
        <!-- 架構說明 -->
        <div class="section" id="architecture">
            <div class="section-header">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                    <rect x="4" y="4" width="10" height="10" rx="2" stroke="#1a73e8" stroke-width="2" fill="none"/>
                    <rect x="18" y="4" width="10" height="10" rx="2" stroke="#34a853" stroke-width="2" fill="none"/>
                    <rect x="11" y="18" width="10" height="10" rx="2" stroke="#f9ab00" stroke-width="2" fill="none"/>
                    <path d="M14 9h4M9 14v4h2M23 14v4h-2" stroke="#5f6368" stroke-width="1.5"/>
                </svg>
                <h2>架構說明</h2>
            </div>

            <div class="flow-diagram">
                <svg width="800" height="300" viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg">
                    <!-- ERP System -->
                    <rect x="50" y="100" width="150" height="100" rx="10" fill="#e8f0fe" stroke="#1a73e8" stroke-width="2"/>
                    <text x="125" y="140" text-anchor="middle" font-weight="bold" fill="#1a73e8">ERP 系統</text>
                    <text x="125" y="165" text-anchor="middle" font-size="12" fill="#5f6368">鼎捷 WFGP/易飛</text>
                    <text x="125" y="185" text-anchor="middle" font-size="12" fill="#5f6368">資料來源</text>

                    <!-- ESB Platform -->
                    <rect x="300" y="50" width="200" height="200" rx="10" fill="#fef7e0" stroke="#f9ab00" stroke-width="2"/>
                    <text x="400" y="90" text-anchor="middle" font-weight="bold" fill="#b06000">ESB 平台</text>

                    <!-- ESB Components -->
                    <rect x="320" y="110" width="160" height="30" rx="5" fill="#fff" stroke="#f9ab00"/>
                    <text x="400" y="130" text-anchor="middle" font-size="12" fill="#5f6368">DataModel 資料模型</text>

                    <rect x="320" y="150" width="160" height="30" rx="5" fill="#fff" stroke="#f9ab00"/>
                    <text x="400" y="170" text-anchor="middle" font-size="12" fill="#5f6368">ProductService 服務</text>

                    <rect x="320" y="190" width="160" height="30" rx="5" fill="#fff" stroke="#f9ab00"/>
                    <text x="400" y="210" text-anchor="middle" font-size="12" fill="#5f6368">欄位映射 & 轉換</text>

                    <!-- MES System -->
                    <rect x="600" y="100" width="150" height="100" rx="10" fill="#e6f4ea" stroke="#34a853" stroke-width="2"/>
                    <text x="675" y="140" text-anchor="middle" font-weight="bold" fill="#137333">MES 系統</text>
                    <text x="675" y="165" text-anchor="middle" font-size="12" fill="#5f6368">eMES</text>
                    <text x="675" y="185" text-anchor="middle" font-size="12" fill="#5f6368">資料接收</text>

                    <!-- Arrows -->
                    <defs>
                        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                            <polygon points="0 0, 10 3.5, 0 7" fill="#5f6368"/>
                        </marker>
                    </defs>

                    <line x1="200" y1="150" x2="290" y2="150" stroke="#5f6368" stroke-width="2" marker-end="url(#arrowhead)"/>
                    <line x1="510" y1="150" x2="590" y2="150" stroke="#5f6368" stroke-width="2" marker-end="url(#arrowhead)"/>

                    <!-- Labels -->
                    <text x="245" y="140" text-anchor="middle" font-size="11" fill="#5f6368">SOAP/REST</text>
                    <text x="550" y="140" text-anchor="middle" font-size="11" fill="#5f6368">JSON/XML</text>
                </svg>
            </div>

            <div class="grid-2">
                <div class="info-box">
                    <h4>🔄 資料流向</h4>
                    <ul class="info-list">
                        <li><span>1. ERP 資料擷取</span><span>SOAP WebService</span></li>
                        <li><span>2. 欄位映射轉換</span><span>ESB 平台處理</span></li>
                        <li><span>3. 資料推送 MES</span><span>REST API</span></li>
                    </ul>
                </div>
                <div class="info-box">
                    <h4>📋 支援協議</h4>
                    <ul class="info-list">
                        <li><span>SOAP WebService</span><span class="badge badge-primary">ERP 整合</span></li>
                        <li><span>REST API</span><span class="badge badge-success">MES 整合</span></li>
                        <li><span>HTTP POST</span><span class="badge badge-info">通用</span></li>
                    </ul>
                </div>
            </div>
        </div>
'''

# 檔案結構說明
html_content += '''
        <!-- 檔案結構說明 -->
        <div class="section" id="file-structure">
            <div class="section-header">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                    <path d="M6 6h8l2 4h10v16H6V6z" stroke="#f9ab00" stroke-width="2" fill="none"/>
                </svg>
                <h2>檔案結構說明</h2>
            </div>

            <p>每個 JSON 檔案都包含以下標準結構：</p>

            <table>
                <thead>
                    <tr>
                        <th>節點名稱</th>
                        <th>說明</th>
                        <th>用途</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><code>monJob</code></td>
                        <td>監控作業</td>
                        <td>定義排程監控任務</td>
                    </tr>
                    <tr>
                        <td><code>dataModel</code></td>
                        <td>資料模型</td>
                        <td>定義資料表結構與 SQL 腳本</td>
                    </tr>
                    <tr>
                        <td><code>dataModelField</code></td>
                        <td>資料模型欄位</td>
                        <td>定義每個資料模型的欄位屬性</td>
                    </tr>
                    <tr>
                        <td><code>dataModelRelate</code></td>
                        <td>資料模型關聯</td>
                        <td>定義資料模型之間的 JOIN 關係</td>
                    </tr>
                    <tr>
                        <td><code>productService</code></td>
                        <td>產品服務</td>
                        <td>定義 Web Service 或 API 端點</td>
                    </tr>
                    <tr>
                        <td><code>productServiceDetail</code></td>
                        <td>服務欄位詳情</td>
                        <td>定義服務的輸入/輸出欄位映射</td>
                    </tr>
                    <tr>
                        <td><code>conditionGroup</code></td>
                        <td>條件群組</td>
                        <td>定義資料過濾條件</td>
                    </tr>
                    <tr>
                        <td><code>dbSetting</code></td>
                        <td>資料庫設定</td>
                        <td>定義資料庫連線資訊</td>
                    </tr>
                </tbody>
            </table>
        </div>
'''

# 服務清單
html_content += '''
        <!-- 服務清單 -->
        <div class="section" id="services">
            <div class="section-header">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                    <circle cx="10" cy="16" r="4" fill="#34a853"/>
                    <circle cx="22" cy="10" r="4" fill="#1a73e8"/>
                    <circle cx="22" cy="22" r="4" fill="#f9ab00"/>
                    <path d="M14 16h4m0 0l-2-4m2 4l-2 4" stroke="#5f6368" stroke-width="2"/>
                </svg>
                <h2>服務清單</h2>
            </div>

            <div class="tabs">
'''

# 生成服務類型標籤
for i, t in enumerate(sorted(svc_by_type.keys())):
    active = 'active' if i == 0 else ''
    html_content += f'                <button class="tab {active}" onclick="showTab(\'{t}\')">{html.escape(t)} ({len(svc_by_type[t])})</button>\n'

html_content += '            </div>\n'

# 生成每個類型的服務表格
for i, t in enumerate(sorted(svc_by_type.keys())):
    active = 'active' if i == 0 else ''
    html_content += f'''
            <div class="tab-content {active}" id="tab-{t}">
                <table>
                    <thead>
                        <tr>
                            <th>服務名稱</th>
                            <th>說明</th>
                            <th>協議</th>
                            <th>格式</th>
                            <th>狀態</th>
                            <th>來源檔案</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    for svc in svc_by_type[t]:
        status_badge = '<span class="badge badge-success">啟用</span>' if svc['enabled'] == 1 else '<span class="badge badge-danger">停用</span>'
        protocol_name = protocol_names.get(svc['protocol'], f"Unknown ({svc['protocol']})")
        format_name = format_names.get(svc['contentFormat'], f"Unknown ({svc['contentFormat']})")

        html_content += f'''                        <tr>
                            <td class="service-name">{html.escape(svc['name'])}</td>
                            <td>{html.escape(svc['desc'])}</td>
                            <td><span class="badge badge-primary">{protocol_name}</span></td>
                            <td><span class="badge badge-info">{format_name}</span></td>
                            <td>{status_badge}</td>
                            <td><code>{html.escape(svc['file'])}</code></td>
                        </tr>
'''

    html_content += '''                    </tbody>
                </table>
            </div>
'''

html_content += '        </div>\n'

# 資料模型區段
html_content += f'''
        <!-- 資料模型 -->
        <div class="section" id="data-models">
            <div class="section-header">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                    <rect x="4" y="8" width="24" height="16" rx="2" stroke="#7627bb" stroke-width="2" fill="none"/>
                    <path d="M4 14h24M12 14v10M20 14v10" stroke="#7627bb" stroke-width="2"/>
                </svg>
                <h2>資料模型</h2>
            </div>

            <p>以下列出所有已定義的資料模型（共 {len(models)} 個）：</p>
'''

# 按表名分組顯示
for table_name in sorted(model_by_table.keys()):
    if not table_name:
        continue
    table_models = model_by_table[table_name]

    html_content += f'''
            <button class="collapsible" onclick="toggleCollapsible(this)">
                <span>
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style="vertical-align: middle; margin-right: 8px;">
                        <rect x="2" y="4" width="16" height="12" rx="1" stroke="#5f6368" stroke-width="1.5" fill="none"/>
                        <path d="M2 8h16" stroke="#5f6368" stroke-width="1.5"/>
                    </svg>
                    <strong>{html.escape(table_name)}</strong>
                    <span class="badge badge-primary" style="margin-left: 10px;">{len(table_models)} 個模型</span>
                </span>
                <svg class="arrow" width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M8 6l4 4-4 4" stroke="#5f6368" stroke-width="2" fill="none"/>
                </svg>
            </button>
            <div class="collapsible-content">
                <table>
                    <thead>
                        <tr>
                            <th>模型代碼</th>
                            <th>模型名稱</th>
                            <th>類型</th>
                            <th>來源</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    for m in table_models:
        view_badge = '<span class="badge badge-warning">View</span>' if m['isView'] == 1 else '<span class="badge badge-success">Table</span>'
        html_content += f'''                        <tr>
                            <td><code>{html.escape(m['modelCode'])}</code></td>
                            <td>{html.escape(m['modelName'])}</td>
                            <td>{view_badge}</td>
                            <td><code>{html.escape(m['file'])}</code></td>
                        </tr>
'''

    html_content += '''                    </tbody>
                </table>
'''

    # 顯示欄位資訊
    for m in table_models:
        model_fields = fields_by_model.get(m['guid'], [])
        if model_fields:
            html_content += f'''
                <div style="margin-top: 15px;">
                    <strong>欄位定義 ({html.escape(m['modelCode'])}):</strong>
                    <table>
                        <thead>
                            <tr>
                                <th>欄位名稱</th>
                                <th>資料型別</th>
                                <th>長度</th>
                                <th>主鍵</th>
                                <th>允許空值</th>
                            </tr>
                        </thead>
                        <tbody>
'''
            for fld in model_fields[:10]:  # 只顯示前10個
                key_badge = '<span class="badge badge-danger">PK</span>' if fld['isKey'] == 1 else ''
                nullable_badge = '<span class="badge badge-success">Yes</span>' if fld['isNullable'] == 1 else '<span class="badge badge-warning">No</span>'
                html_content += f'''                            <tr>
                                <td><code>{html.escape(str(fld['fieldName']))}</code></td>
                                <td>{html.escape(str(fld['dataType']))}</td>
                                <td>{fld['length']}</td>
                                <td>{key_badge}</td>
                                <td>{nullable_badge}</td>
                            </tr>
'''
            if len(model_fields) > 10:
                html_content += f'''                            <tr>
                                <td colspan="5" style="text-align: center; color: #5f6368;">... 還有 {len(model_fields) - 10} 個欄位</td>
                            </tr>
'''
            html_content += '''                        </tbody>
                    </table>
                </div>
'''

    # 如果有 SQL Script，顯示出來
    for m in table_models:
        if m['sqlScript'] and m['sqlScript'].strip():
            html_content += f'''
                <div style="margin-top: 15px;">
                    <strong>SQL Script ({html.escape(m['modelCode'])}):</strong>
                    <div class="code-block">{html.escape(m['sqlScript'])}</div>
                </div>
'''

    html_content += '            </div>\n'

html_content += '        </div>\n'

# 資料庫設定
if db_settings:
    html_content += '''
        <!-- 資料庫設定 -->
        <div class="section" id="db-settings">
            <div class="section-header">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                    <ellipse cx="16" cy="10" rx="10" ry="4" stroke="#1a73e8" stroke-width="2" fill="none"/>
                    <path d="M6 10v12c0 2.2 4.5 4 10 4s10-1.8 10-4V10" stroke="#1a73e8" stroke-width="2" fill="none"/>
                    <path d="M6 16c0 2.2 4.5 4 10 4s10-1.8 10-4" stroke="#1a73e8" stroke-width="2" fill="none"/>
                </svg>
                <h2>資料庫設定</h2>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>代碼</th>
                        <th>類型</th>
                        <th>IP</th>
                        <th>資料庫名稱</th>
                        <th>Port</th>
                        <th>來源</th>
                    </tr>
                </thead>
                <tbody>
'''
    db_types = {0: 'SQL Server', 1: 'Oracle', 2: 'MySQL', 3: 'PostgreSQL'}

    for db in db_settings:
        db_type_name = db_types.get(db['dbType'], f"Unknown ({db['dbType']})")
        html_content += f'''                    <tr>
                        <td><code>{html.escape(str(db['dbCode']))}</code></td>
                        <td><span class="badge badge-primary">{db_type_name}</span></td>
                        <td>{html.escape(str(db['dbIP']))}</td>
                        <td>{html.escape(str(db['dbName']))}</td>
                        <td>{html.escape(str(db['dbPort']))}</td>
                        <td><code>{html.escape(db['file'])}</code></td>
                    </tr>
'''

    html_content += '''                </tbody>
            </table>
        </div>
'''

# 欄位對應說明
html_content += '''
        <!-- 欄位對應說明 -->
        <div class="section" id="field-mapping">
            <div class="section-header">
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                    <path d="M6 10h8v4H6v-4zm18 0h2v4h-2v-4zM14 12h6" stroke="#34a853" stroke-width="2"/>
                    <path d="M6 18h8v4H6v-4zm18 0h2v4h-2v-4zM14 20h6" stroke="#f9ab00" stroke-width="2"/>
                </svg>
                <h2>欄位對應說明</h2>
            </div>

            <div class="grid-2">
                <div class="info-box">
                    <h4>📝 productService 主要欄位</h4>
                    <ul class="info-list">
                        <li><span>SERVICENAME</span><span>服務名稱</span></li>
                        <li><span>SERVICEDESC</span><span>服務說明</span></li>
                        <li><span>SERVICEPROTOCOL</span><span>通訊協議 (0=HTTP, 1=SOAP, 2=WS)</span></li>
                        <li><span>CONTENTFORMAT</span><span>內容格式 (0=XML, 1=JSON)</span></li>
                        <li><span>ISENABLE</span><span>是否啟用 (0=否, 1=是)</span></li>
                        <li><span>SERVICEURL</span><span>服務端點 URL</span></li>
                        <li><span>RETRYCOUNT</span><span>重試次數</span></li>
                        <li><span>RETRYCYCLE</span><span>重試間隔 (毫秒)</span></li>
                    </ul>
                </div>
                <div class="info-box">
                    <h4>📋 dataModel 主要欄位</h4>
                    <ul class="info-list">
                        <li><span>TABLENAME</span><span>資料表名稱</span></li>
                        <li><span>MODELCODE</span><span>模型代碼 (唯一識別)</span></li>
                        <li><span>MODELNAME</span><span>模型名稱 (中文說明)</span></li>
                        <li><span>SQLSCRIPT</span><span>自訂 SQL 查詢</span></li>
                        <li><span>ISVIEW</span><span>是否為 View (0=否, 1=是)</span></li>
                        <li><span>ROWLIMIT</span><span>資料筆數限制</span></li>
                    </ul>
                </div>
                <div class="info-box">
                    <h4>🔧 dataModelField 主要欄位</h4>
                    <ul class="info-list">
                        <li><span>FIELDNAME</span><span>欄位名稱</span></li>
                        <li><span>DATATYPE</span><span>資料型別 (string/int/datetime)</span></li>
                        <li><span>LENGTH</span><span>欄位長度</span></li>
                        <li><span>ISKEY</span><span>是否為主鍵</span></li>
                        <li><span>ISNULLABLE</span><span>是否允許空值</span></li>
                        <li><span>ISSTATUSCOLUMN</span><span>是否為狀態欄位</span></li>
                    </ul>
                </div>
                <div class="info-box">
                    <h4>⚙️ productServiceDetail 主要欄位</h4>
                    <ul class="info-list">
                        <li><span>fieldname</span><span>欄位名稱</span></li>
                        <li><span>fieldtype</span><span>欄位類型</span></li>
                        <li><span>mappingfield</span><span>映射欄位</span></li>
                        <li><span>isnecessary</span><span>是否必填</span></li>
                        <li><span>iskey</span><span>是否為 Key</span></li>
                        <li><span>fixedvalue</span><span>固定值</span></li>
                    </ul>
                </div>
            </div>
        </div>
'''

# 頁尾
html_content += '''
        <footer>
            <p>📄 ESB 平台設定檔說明文件 | 版本 1.7.0 | 自動生成於 2026-03-20</p>
            <p>此文件由 JSON 設定檔自動解析生成</p>
        </footer>
    </div>

    <script>
        function showTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => {
                el.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(el => {
                el.classList.remove('active');
            });
            document.getElementById('tab-' + tabId).classList.add('active');
            event.target.classList.add('active');
        }

        function toggleCollapsible(element) {
            element.classList.toggle('active');
            var content = element.nextElementSibling;
            content.classList.toggle('active');
        }
    </script>
</body>
</html>
'''

# 寫入 HTML 檔案
with open('ESB_Configuration_Documentation.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('Done!')
