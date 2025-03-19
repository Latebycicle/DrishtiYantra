import { View, StyleSheet } from 'react-native';
import NavigationButton from '../components/NavigationButton';
import { speak } from 'expo-speech';
import { StackScreenProps } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/types';

type Props = StackScreenProps<RootStackParamList, 'Settings'>;

export default function SettingsScreen({ navigation }: Props) {
  return (
    <View style={styles.container}>
      <NavigationButton
        label="English"
        onPress={() => {
          speak("Language set to English");
          console.log('Change to English');
        }}
      />
      <NavigationButton
        label="ಕನ್ನಡ (Kannada)"
        onPress={() => {
          speak("Language set to Kannada");
          console.log('Change to Kannada');
        }}
      />
      <NavigationButton
        label="Back to Home"
        onPress={() => navigation.goBack()}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center'
  }
});