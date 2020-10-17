const VERSION = 6;

const SPREADSHEET_ID = '1J2wfHYgB-JK1mwckb2PYxwZ0fU3SKbnuZhndt9LLiz8';
const SHEET_NAME = 'Passwords';

const ERROR = {
  INVALID_JSON: {
    code: 1,
    message: `無効なJSON形式です。`,
  },
  PASSWORD_NOT_SET: {
    code: 2,
    message: `パスワードが必要です。`,
  },
  PASSWORD_NOT_EXIST: {
    code: 3,
    message: `パスワードが存在しません。`,
  },
  PASSWORD_NOT_YET_VALID: {
    code: 4,
    message: `パスワードの有効期限が始まっていません。`,
  },
  PASSWORD_EXPIRED: {
    code: 5,
    message: `パスワードの有効期限が切れています。`,
  },
} as const;

function doGet(e: GoogleAppsScript.Events.DoGet): GoogleAppsScript.Content.TextOutput {
  const result = authenticate(e);
  const content = JSON.stringify({
    version: VERSION,
    ...result,
  });
  Logger.log(content);
  const output = ContentService.createTextOutput();
  output.setMimeType(ContentService.MimeType.JSON);
  output.setContent(content);
  return output;
}

function authenticate(e: GoogleAppsScript.Events.DoGet) {
  const peerId = e.parameter['peerId'];
  const password = e.parameter['password'];
  if (!password) {
    return {
      ...ERROR.PASSWORD_NOT_SET,
    };
  }
  const currentTime = Date.now();
  if (peerId === 'master') {
    if (password === PropertiesService.getScriptProperties().getProperty('MASTER_PASSWORD')) {
      const timestamp = Math.floor(currentTime / 1000);
      // ttl must be between 600 and 90000
      const ttl = 90000;
      return {
        code: 0,
        startTime: timestamp * 1000,
        endTime: (timestamp + ttl) * 1000,
        credential: calculateCredential(peerId, timestamp, ttl),
      };
    } else {
      return {
        ...ERROR.PASSWORD_NOT_EXIST,
      };
    }
  } else {
    const found = getPasswords().find((item) => item.password === password);
    if (!found) {
      return {
        ...ERROR.PASSWORD_NOT_EXIST,
      };
    }
    const startTime = new Date(found.startTime).getTime();
    const endTime = new Date(found.endTime).getTime();
    if (currentTime < startTime) {
      return {
        ...ERROR.PASSWORD_NOT_YET_VALID,
        startTime: found.startTime,
        endTime: found.endTime,
      };
    } else if (endTime < currentTime) {
      return {
        ...ERROR.PASSWORD_EXPIRED,
        startTime: found.startTime,
        endTime: found.endTime,
      };
    }
    // ttl must be between 600 and 90000
    const ttl = 90000;
    const timestamp = Math.min(
      Math.floor(endTime / 1000) - ttl,
      Math.floor(currentTime / 1000),
    );
    return {
      code: 0,
      startTime: found.startTime,
      endTime: found.endTime,
      credential: calculateCredential(peerId, timestamp, ttl),
    };
  }
}

function getPasswords() {
  const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = spreadsheet.getSheetByName(SHEET_NAME);
  const range = sheet.getDataRange();
  const values = range.getValues();
  return values.map(([password, startTime, endTime]: string[]) => ({
    password,
    startTime,
    endTime,
  }));
}

function calculateCredential(peerId: string, timestamp: number, ttl: number) {
  const secretKey = PropertiesService.getScriptProperties().getProperty('SKYWAY_SECRET_KEY');
  const hash = Utilities.computeHmacSha256Signature(`${timestamp}:${ttl}:${peerId}`, secretKey);
  const authToken = Utilities.base64Encode(hash);
  return {
    peerId,
    timestamp,
    ttl,
    authToken,
  };
}
