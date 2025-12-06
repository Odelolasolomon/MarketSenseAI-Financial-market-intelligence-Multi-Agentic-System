import { google } from "@ai-sdk/google";
import { streamText } from "ai";

export const runtime = "edge";

export async function POST(req: Request) {
    const { messages } = await req.json();
    const lastMessage = messages[messages.length - 1] as any;
    const textContent = lastMessage.parts?.find((part: any) => part.type === "text")?.text || lastMessage.content || "";

    try {
        // Get backend URL from environment, validate it exists
        const backendUrl = process.env.NEXT_PUBLIC_BASE_API_URL;
        if (!backendUrl) {
            console.error("NEXT_PUBLIC_BASE_API_URL environment variable is not set");
            return new Response(
                JSON.stringify({
                    error: 'Backend API URL is not configured. Please set NEXT_PUBLIC_BASE_API_URL.',
                }),
                { status: 500 }
            );
        }

        // Build the analyze endpoint URL
        const analyzeUrl = `${backendUrl}/analyze`;
        console.log(`Calling backend: ${analyzeUrl}`);

        const response = await fetch(analyzeUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                query: textContent,
                timeframe: "medium"
            }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error(`Backend error (${response.status}): ${errorText}`);
            return new Response(
                JSON.stringify({
                    error: `Backend returned ${response.status}: ${errorText}`,
                }),
                { status: response.status }
            );
        }

        const analysisData = await response.json();
        console.log("Response from backend:", analysisData);

        const result = streamText({
            model: google("gemini-2.5-flash"),
            system: "You are MarketSenseAI, a professional financial analyst assistant. Format your responses in clear, structured sections using markdown. First give a summary of the analysis to the user and then present the details in an easy-to-understand format. Be concise but comprehensive.",
            messages: [
                {
                    role: 'user',
                    content: `Based on this comprehensive market analysis, provide a clear investment recommendation:

${JSON.stringify(analysisData, null, 2)}

Format your response with clear sections and actionable insights.`,
                },
            ],
        });

        return result.toUIMessageStreamResponse();
    }
    catch (error) {
        console.error("Error processing request:", error);
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return new Response(
            JSON.stringify({
                error: `Failed to process the request: ${errorMessage}`,
            }),
            { status: 500 }
        );
    }
}