function doGet(): GoogleAppsScript.Content.TextOutput {
  const output = ContentService.createTextOutput();
  output.setMimeType(ContentService.MimeType.JSON);
  output.setContent(JSON.stringify({
    text: 'hello'
  }));
  return output;
}
