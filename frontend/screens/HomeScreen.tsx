import { View, StyleSheet } from 'react-native';
import NavigationButton from '../components/NavigationButton';
import { speak } from 'expo-speech';
import { StackScreenProps } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/types';

type Props = StackScreenProps<RootStackParamList, 'Home'>;

export default function HomeScreen({ navigation }: Props) {
  return (
    <View style={styles.container}>
      <NavigationButton
        label="Detect Colors"
        onPress={() => {
          speak("Navigating to Color Detection");
          navigation.navigate('ColorDetection');
        }}
        bgcolor='#648fff'
        textcolor='#fe6100'
      />

      <NavigationButton
        label="Text To Speech"
        onPress={() => {
          speak("Navigating to Text to Speech");
          navigation.navigate('TextToSpeech');
        }}
        bgcolor='#000000'
        textcolor='#ffb000'
      />

      <NavigationButton
        label="Settings"
        onPress={() => {
          speak("Navigating to Settings");
          navigation.navigate('Settings');
        }}
        bgcolor='#785ef0'
        textcolor='#000000'
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