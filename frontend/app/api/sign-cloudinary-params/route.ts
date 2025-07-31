import { NextRequest, NextResponse } from 'next/server'
import { v2 as cloudinary } from 'cloudinary'

// Configure Cloudinary
cloudinary.config({
    cloud_name: process.env.NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME,
    api_key: process.env.CLOUDINARY_API_KEY,
    api_secret: process.env.CLOUDINARY_API_SECRET,
})

export async function POST(request: NextRequest) {
    try {
        const { paramsToSign } = await request.json()

        // Sign the parameters
        const signature = cloudinary.utils.api_sign_request(
            paramsToSign,
            process.env.CLOUDINARY_API_SECRET!
        )

        return NextResponse.json({
            signature,
            timestamp: paramsToSign.timestamp,
        })
    } catch (error) {
        console.error('Error signing Cloudinary parameters:', error)
        return NextResponse.json(
            { error: 'Failed to sign upload parameters' },
            { status: 500 }
        )
    }
}
