function doGet(e: GoogleAppsScript.Events.AppsScriptHttpRequestEvent): GoogleAppsScript.Content.TextOutput {
  const peerId = e.parameter['peerId'];
  const timestamp = Math.floor(Date.now() / 1000);
  const ttl = 300;
  const credential = {
    peerId,
    timestamp,
    ttl,
    authToken: calculateAuthToken(peerId, timestamp, ttl),
  };
  const output = ContentService.createTextOutput();
  output.setMimeType(ContentService.MimeType.JSON);
  const content = JSON.stringify({
    code: 0,
    credential,
  });
  Logger.log(content);
  output.setContent(content);
  return output;
}

function calculateAuthToken(peerId: string, timestamp: number, ttl: number): string {
  const secretKey = PropertiesService.getScriptProperties().getProperty('SKYWAY_SECRET_KEY');
  const hash = Utilities.computeHmacSha256Signature(`${timestamp}:${ttl}:${peerId}`, secretKey);
  return Utilities.base64Encode(hash);
}
