import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  ScrollView,
  Text,
  TextInput,
  StyleSheet,
  Picker,
  Button,
  Image,
  Alert,
  TouchableOpacity
} from 'react-native';

import Title from '../components/Title'
import text from '../constants/text'
import Colors from '../constants/Colors';


const RegisterScreen = props => {
  const [username, setUsername] = useState('');
  const [userPassword, setUserPassword] = useState('');
  const [userPasswordAuthentication, setUserPasswordAuthentication] = useState('');

  const validatePassword = () => {
    if (userPassword === userPasswordAuthentication) {
      return true;
    }
    else {
      return false;
    }
  }
  const passwordLengthValidation = () => {
    const passLen = userPassword.length
    if (passLen < 6 || passLen > 8) {
      return false;
    }
    else {
      return true;
    }
  }
  const validateUsername = () => {
    if (/^[a-zA-Z]+$/.test(username)) {
      return true;
    }
    else {
      return false;
    }
  }

  const handleRegister = async () => {
    const validatingPassword = validatePassword();
    const passwordLengthValidating = passwordLengthValidation();
    const validatingUsername = validateUsername();
    console.log("===============================")
    console.log("validate password: ", validatingPassword);
    console.log("validate password length: ", passwordLengthValidating);
    console.log("validate username: ", validatingUsername);

    if (validatingUsername && passwordLengthValidating && validatingPassword) {
      console.log("we all good now send somthing to matan!")

      const response = await fetch('https://cureona.herokuapp.com/Registration', {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_name: username,
          password: userPassword,
          type: "customer"
        }),
      });

      const resData = await response.json();
      console.log(resData);
      if (resData.state === "success") {
        props.navigation.popToTop();
        props.navigation.navigate({
          routeName: "UserScreen",
          params: {
            username: username,
          }
        })
      }
      else {
        Alert.alert("pleas check your username and password.")
      }

    }
  }

  return (
    <ScrollView>
      <Title title={text.register} />
      <View style={styles.form}>
        <View style={styles.formControl}>
          <Text style={styles.label}>{text.username}</Text>
          <TextInput
            style={styles.input}
            value={username}
            onChangeText={text => setUsername(text)}
            returnKeyType="next"

          />
        </View>
        <View style={styles.formControl}>
          <Text style={styles.label}>{text.password}</Text>
          <TextInput
            style={styles.input}
            value={userPassword}
            onChangeText={text => setUserPassword(text)}
            secureTextEntry={true}

          />
        </View>
        <View style={styles.formControl}>
          <Text style={styles.label}>{text.passwordAuthentication}</Text>
          <TextInput
            style={styles.input}
            value={userPasswordAuthentication}
            onChangeText={text => setUserPasswordAuthentication(text)}
            secureTextEntry={true}

          />
        </View>
        <View style={styles.gap} />
        <Button color={Colors.primaryColor} title={text.register} onPress={() => { handleRegister() }} />

      </View>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  form: {
    margin: 20,
  },
  formControl: {
    width: '100%'
  },
  label: {
    marginTop: 30,
    marginVertical: 8,
    fontWeight: 'bold',
    fontSize: 18,
  },
  input: {
    paddingHorizontal: 2,
    paddingVertical: 5,
    borderBottomColor: '#ccc',
    borderBottomWidth: 1
  },
  Instructions:
  {
    marginVertical: 8,
    color: 'red',
    fontSize: 12,
  },
  gap: {
    margin: 50,
  },
});



export default RegisterScreen;