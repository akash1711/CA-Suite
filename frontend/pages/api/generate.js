import axios from 'axios';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { prompt } = req.body;

  try {
    const response = await axios.post(process.env.NEXT_PUBLIC_BACKEND_URL + '/generate_reply', {
      message: prompt,
    });

    const reply = response.data.reply || '';
    res.status(200).json({ reply });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Error generating reply' });
  }
}
