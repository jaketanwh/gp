function GetQQMd5Rsa(password, salt, verifycode) {

    //return salt;
    //return $.Encryption.getRSAEncryption(password, verifycode);
    return $.Encryption.getEncryption(password,uin2hex(salt), verifycode);
//    return typeof($.Encryption.getEncryption);
};

function uin2hex(str) {
    var maxLength = 16;
    var hex = parseInt(str).toString(16);
    var len = hex.length;
    for (var i = len; i < maxLength; i++) {
        hex = '0' + hex
    }
    var arr = [];
    for (var j = 0; j < maxLength; j += 2) {
        arr.push('\\x' + hex.substr(j, 2))
    }
    var result = arr.join('');
    eval('result="' + result + '"');
    return result
}