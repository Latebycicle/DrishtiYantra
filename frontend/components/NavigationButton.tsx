import { Pressable, Text, StyleSheet } from 'react-native';
import { speak } from 'expo-speech';

export default function NavigationButton({ label='', onPress, bgcolor='#0072b2', textcolor='#e69f00' }) {
  return (
    <Pressable
      style={({ pressed }) => [
        styles.button,
        { backgroundColor: pressed ?   '#ffffff' : bgcolor}
      ]}
      onPress={() => {
        speak(label); // Voice feedback
        onPress();
      }}
      accessibilityLabel={label}
      accessibilityRole="button"
    >
      <Text style={[styles.text, { color: textcolor }]}>{label}</Text> 
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    padding: 45, // Increased padding for larger button
    margin: 12,  // Increased margin
    borderRadius: 10,
    minWidth: 250, // Set a minimum width
    alignItems: 'center', // Center text inside the button
    backgroundColor: '#000000', 
  },
  text: {
    fontWeight: 'bold',
    fontSize: 40, // Slightly increased font size for better visibility
    textAlign: 'center'
  }
});