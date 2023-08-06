from setuptools import setup

setup(
    name='mySecrets',
    version='0.9.1',
    author='Tiancheng Jiao',
    author_email='jtc1246@outlook.com',
    url='https://github.com/jtc1246/mySecrets',
    description='Very secure hash and symmetrical encryption',
    packages=['mySecrets'],
    python_requires='>=3',
    platforms=["all"],
    license='GPL-2.0 License',
    entry_points={
        'console_scripts': [
            'getHash=mySecrets:getHash',
            'encrypt=mySecrets:encrypt',
            'decrypt=mySecrets:decrypt',
            'hexToStr=mySecrets:hexToStr',
            'toHex=mySecrets:toHex',
            'hexToJtc64=mySecrets:hexToJtc64',
            'strToJtc64=mySecrets:strToJtc64',
            'jtc64ToHex=mySecrets:jtc64ToHex',
            'jtc64ToStr=mySecrets:jtc64ToStr',
            'NotHexError=mySecrets:NotHexError',
            'NotJtc64Error=mySecrets:NotJtc64Error',
            'InputError=mySecrets:InputError',
            'InvalidCiphertextError=mySecrets:InvalidCiphertextError',
            'VersionNotSupportError=mySecrets:VersionNotSupportError',
            'PasswordWrongError=mySecrets:PasswordWrongError'
        ]
    }
)

