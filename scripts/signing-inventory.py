"""Read-only Apple inventory. Never creates/revokes credentials or uploads binaries."""
import os, time, json, urllib.request, urllib.error, urllib.parse, base64, plistlib, subprocess
import jwt
key = os.environ['ASC_KEY_P8'].replace('\\n', '\n')
token = jwt.encode({'iss': os.environ['ASC_ISSUER_ID'], 'iat': int(time.time()), 'exp': int(time.time()) + 600, 'aud':'appstoreconnect-v1'}, key, algorithm='ES256', headers={'kid':os.environ['ASC_KEY_ID'],'typ':'JWT'})
def get(path):
    req = urllib.request.Request('https://api.appstoreconnect.apple.com'+path, headers={'Authorization':'Bearer '+token}, method='GET')
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.load(response)
def attrs(item, names):
    return {'id':item['id'], **{n:item['attributes'].get(n) for n in names}}
result={'mode':'read-only GET; no credential mutations or store upload', 'certificates':[], 'apps':[]}
certs=get('/v1/certificates?limit=200')['data']
result['certificates']=[attrs(c,['name','certificateType','expirationDate']) for c in certs]
for identifier, appid in [('com.beno74.landscraper','6828032990'),('com.beno74.shapescraper','6826044452')]:
    app={'identifier':identifier,'profiles':[], 'versions':[]}
    bids=get('/v1/bundleIds?filter[identifier]='+identifier)['data']
    for bid in bids:
        app['bundleIdResource']=bid['id']
        profiles=get('/v1/bundleIds/'+bid['id']+'/profiles?limit=200')['data']
        for profile in profiles:
            a=profile['attributes']
            if a.get('profileType')!='IOS_APP_STORE': continue
            p=attrs(profile,['name','profileType','profileState','expirationDate','uuid'])
            if a.get('profileContent'):
                decoded=subprocess.run(['security','cms','-D'], input=base64.b64decode(a['profileContent']), capture_output=True, check=True)
                content=plistlib.loads(decoded.stdout)
                ent=content.get('Entitlements',{})
                p['ageEntitlement']=ent.get('com.apple.developer.declared-age-range')
                p['applicationIdentifier']=ent.get('application-identifier')
                p['teamIdentifier']=content.get('TeamIdentifier')
                p['getTaskAllow']=ent.get('get-task-allow')
            app['profiles'].append(p)
    app['versions']=[attrs(v,['versionString','appStoreState','platform']) for v in get('/v1/apps/'+appid+'/appStoreVersions?limit=200')['data']]
    result['apps'].append(app)
with open(os.environ['INVENTORY_OUTPUT'],'w') as out: json.dump(result,out,indent=2)
print('Sanitized read-only certificate/profile/version inventory completed.')
