"""Owner-approved additive signing assets only. Never revokes, submits, or uploads an app.
Run once with a CSR whose private key stays on the owner's Mac. On partial failure,
retain the recorded certificate ID; do not rerun certificate creation automatically.
"""
import os, time, json, base64, pathlib, urllib.request, plistlib, subprocess
import jwt
if os.environ.get('OWNER_APPROVED_SIGNING') != 'create-one-distribution-and-two-profiles':
    raise SystemExit('Explicit owner approval required; nothing changed.')
out = pathlib.Path(os.environ['SIGNING_OUTPUT']); out.mkdir(parents=True, exist_ok=True)
csr = os.environ['SIGNING_CSR_PEM']
if not csr.startswith('-----BEGIN CERTIFICATE REQUEST-----'):
    raise SystemExit('Expected public CSR, never a private key.')
token = jwt.encode({'iss':os.environ['ASC_ISSUER_ID'], 'iat':int(time.time()), 'exp':int(time.time())+600, 'aud':'appstoreconnect-v1'}, os.environ['ASC_KEY_P8'].replace('\\n','\n'), algorithm='ES256', headers={'kid':os.environ['ASC_KEY_ID'],'typ':'JWT'})
def api(method, path, data=None):
    req = urllib.request.Request('https://api.appstoreconnect.apple.com'+path, data=json.dumps(data).encode() if data else None, method=method, headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=45) as response: return json.load(response)
report={'certificate':None,'profiles':[],'revoked_existing_assets':False,'uploaded_app':False}
def save(): (out/'created-signing-assets.json').write_text(json.dumps(report,indent=2))
# A supplied ID supports explicit recovery after partial completion, without creating duplicates.
certid=os.environ.get('EXISTING_NEW_CERTIFICATE_ID')
if certid:
    cert=api('GET','/v1/certificates/'+certid)['data']
else:
    cert=api('POST','/v1/certificates',{'data':{'type':'certificates','attributes':{'certificateType':'DISTRIBUTION','csrContent':csr}}})['data']
certid=cert['id']; a=cert['attributes']
if a.get('certificateType') not in ('DISTRIBUTION','IOS_DISTRIBUTION'): raise SystemExit('Unexpected signing certificate type')
report['certificate']={'id':certid,'type':a['certificateType'],'expiration':a['expirationDate']}; save()
(out/'distribution.cer').write_bytes(base64.b64decode(a['certificateContent']))
for game,bid in [('landscraper','9GL667BRBS'),('shapescraper','B7Y6G6N3KA')]:
    name='BENO74 '+game+' App Store age-enabled 20261119'
    existing=api('GET','/v1/bundleIds/'+bid+'/profiles?limit=200')['data']
    if any(p['attributes'].get('name')==name for p in existing):
        raise SystemExit('Named profile already exists; inspect it instead of creating another.')
    profile=api('POST','/v1/profiles',{'data':{'type':'profiles','attributes':{'name':name,'profileType':'IOS_APP_STORE'},'relationships':{'bundleId':{'data':{'type':'bundleIds','id':bid}},'certificates':{'data':[{'type':'certificates','id':certid}]}}}})['data']
    a=profile['attributes']; data=base64.b64decode(a['profileContent'])
    (out/(game+'.mobileprovision')).write_bytes(data)
    decoded=subprocess.run(['security','cms','-D'], input=data,capture_output=True,check=True)
    ent=plistlib.loads(decoded.stdout)['Entitlements']
    report['profiles'].append({'game':game,'id':profile['id'],'name':a['name'],'state':a['profileState'],'uuid':a['uuid'],'ageEntitlement':ent.get('com.apple.developer.declared-age-range'),'applicationIdentifier':ent.get('application-identifier'),'getTaskAllow':ent.get('get-task-allow')}); save()
    if a['profileState']!='ACTIVE' or ent.get('com.apple.developer.declared-age-range') is not True or ent.get('get-task-allow') is not False or ent.get('application-identifier')!='C46AXBT6CZ.com.beno74.'+game:
        raise SystemExit('New profile failed entitlement/state checks; do not sign or release.')
print('Created and checked additive signing assets. No app uploaded.')
