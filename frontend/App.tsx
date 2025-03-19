import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import HomeScreen from './screens/HomeScreen';
import ColorDetectionScreen from './screens/ColorDetectionScreen';
import SettingsScreen from './screens/SettingsScreen';
import TextToSpeechScreen from './screens/TextToSpeechScreen';
import { RootStackParamList } from './navigation/types';

const Stack = createStackNavigator<RootStackParamList>();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="ColorDetection" component={ColorDetectionScreen} />
        <Stack.Screen name="Settings" component={SettingsScreen} />
        <Stack.Screen name="TextToSpeech" component={TextToSpeechScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}