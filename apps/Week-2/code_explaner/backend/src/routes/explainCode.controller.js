import { explainCodeWithAI } from '../utils/ai.utils.js';

export const explainCode = async (req, res) => {
    try {
        const { code, language } = req.body;

        if (!code) {
            return res.status(400).json({
                success: false,
                error: 'Code is required',
            });
        }

        const explanation = await explainCodeWithAI(code, language);
        return res.status(200).json({
            success: true,
            language: language || '',
            explanation,
        });
    } catch (error) {
        console.error('ERROR: ', error);
        return res.status(500).json({
            success: false,
            message: error instanceof Error ? error.message : 'Internal server error',
        });
    }
};
