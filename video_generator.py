"""
Video Generator
Handles video creation using AI services
"""

import os
import logging
import json
import requests
import subprocess
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import anthropic
import openai

logger = logging.getLogger(__name__)


class VideoGenerator:
    """Generate videos using AI services and video editing tools"""
    
    def __init__(self, config: Dict):
        """
        Initialize video generator
        
        Args:
            config: Configuration dictionary with video generation settings
        """
        self.config = config
        self.output_dir = Path("output_videos")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize AI clients based on config
        self.ai_provider = config.get('ai_provider', 'openai')
        self._init_ai_client()
        
    def _init_ai_client(self):
        """Initialize AI client based on provider"""
        if self.ai_provider == 'openai':
            self.ai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        elif self.ai_provider == 'anthropic':
            self.ai_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        else:
            logger.warning(f"Unknown AI provider: {self.ai_provider}")
    
    def create_music_and_intro(self, topic: str, prompts: str) -> Dict:
        """
        Generate background music and intro video
        
        Args:
            topic: Video topic
            prompts: Additional prompts for customization
            
        Returns:
            Dictionary with paths to music and intro files
        """
        logger.info(f"Creating music and intro for: {topic}")
        
        result = {
            'music_path': None,
            'intro_path': None
        }
        
        try:
            # Generate script and visual plan
            script_data = self._generate_script(topic, prompts)
            
            # Generate background music
            music_path = self._generate_music(
                mood=script_data.get('mood', 'upbeat'),
                duration=self.config.get('video_duration', 60)
            )
            result['music_path'] = music_path
            
            # Generate intro video
            intro_path = self._generate_intro(
                topic=topic,
                visual_style=script_data.get('visual_style', 'modern')
            )
            result['intro_path'] = intro_path
            
            logger.info("Music and intro created successfully")
            
        except Exception as e:
            logger.error(f"Error creating music and intro: {str(e)}")
            raise
        
        return result
    
    def _generate_script(self, topic: str, prompts: str) -> Dict:
        """
        Generate video script using AI
        
        Args:
            topic: Video topic
            prompts: Additional context
            
        Returns:
            Dictionary containing script and metadata
        """
        logger.info("Generating video script")
        
        system_prompt = """You are an expert video script writer. Create engaging, 
        concise scripts for YouTube videos. Include visual descriptions, narration, 
        and pacing suggestions. Return your response in JSON format with the following structure:
        {
            "title": "video title",
            "script": "full narration script",
            "scenes": [{"narration": "text", "visuals": "description", "duration": seconds}],
            "mood": "upbeat/calm/dramatic/etc",
            "visual_style": "modern/cinematic/minimalist/etc",
            "estimated_duration": seconds
        }"""
        
        user_prompt = f"""Create a video script for the following topic:
        
        Topic: {topic}
        
        Additional Requirements: {prompts}
        
        The video should be approximately {self.config.get('video_duration', 60)} seconds long.
        Make it engaging and suitable for YouTube."""
        
        try:
            if self.ai_provider == 'anthropic':
                response = self.ai_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2000,
                    messages=[
                        {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                    ]
                )
                script_text = response.content[0].text
            else:  # OpenAI
                response = self.ai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )
                script_text = response.choices[0].message.content
            
            # Parse JSON response
            # Remove markdown code blocks if present
            script_text = script_text.replace('```json', '').replace('```', '').strip()
            script_data = json.loads(script_text)
            
            logger.info(f"Generated script: {script_data['title']}")
            return script_data
            
        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            # Return a basic fallback
            return {
                "title": topic,
                "script": f"A video about {topic}",
                "scenes": [],
                "mood": "upbeat",
                "visual_style": "modern",
                "estimated_duration": 60
            }
    
    def _generate_music(self, mood: str, duration: int) -> Optional[str]:
        """
        Generate or select background music
        
        Args:
            mood: Mood of the music
            duration: Duration in seconds
            
        Returns:
            Path to music file
        """
        logger.info(f"Generating {mood} music for {duration} seconds")
        
        # For now, create a placeholder music file
        # In production, integrate with music generation APIs like:
        # - Mubert API
        # - AIVA
        # - Soundraw
        # - Or use royalty-free music libraries
        
        music_path = self.output_dir / f"music_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        
        # Create a silent audio file as placeholder (using FFmpeg)
        try:
            subprocess.run([
                'ffmpeg', '-f', 'lavfi', '-i', f'anullsrc=r=44100:cl=stereo',
                '-t', str(duration), '-c:a', 'libmp3lame', '-b:a', '128k',
                str(music_path), '-y'
            ], check=True, capture_output=True)
            
            logger.info(f"Music file created: {music_path}")
            return str(music_path)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating music file: {str(e)}")
            return None
    
    def _generate_intro(self, topic: str, visual_style: str) -> Optional[str]:
        """
        Generate intro video
        
        Args:
            topic: Video topic for intro text
            visual_style: Visual style for intro
            
        Returns:
            Path to intro video file
        """
        logger.info(f"Generating intro with style: {visual_style}")
        
        intro_path = self.output_dir / f"intro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        
        # Create a simple intro using FFmpeg
        # In production, use video generation APIs like:
        # - D-ID
        # - Synthesia
        # - Runway ML
        # - Pictory
        
        try:
            # Create a 5-second intro with text
            subprocess.run([
                'ffmpeg',
                '-f', 'lavfi', '-i', 'color=c=black:s=1920x1080:d=5',
                '-vf', f"drawtext=text='{topic}':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
                '-c:v', 'libx264', '-t', '5', '-pix_fmt', 'yuv420p',
                str(intro_path), '-y'
            ], check=True, capture_output=True)
            
            logger.info(f"Intro video created: {intro_path}")
            return str(intro_path)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating intro: {str(e)}")
            return None
    
    def generate_full_video(self, topic: str, prompts: str, 
                          music_path: Optional[str] = None,
                          intro_path: Optional[str] = None) -> Dict:
        """
        Generate complete video with all components
        
        Args:
            topic: Video topic
            prompts: Additional prompts
            music_path: Path to background music
            intro_path: Path to intro video
            
        Returns:
            Dictionary with video information
        """
        logger.info(f"Generating full video for: {topic}")
        
        try:
            # Generate full script if not already done
            script_data = self._generate_script(topic, prompts)
            
            # Generate scenes
            scene_videos = self._generate_scenes(script_data['scenes'])
            
            # Generate voiceover
            voiceover_path = self._generate_voiceover(script_data['script'])
            
            # Combine all elements
            final_video_path = self._combine_video_elements(
                scene_videos=scene_videos,
                voiceover=voiceover_path,
                music=music_path,
                intro=intro_path,
                topic=topic
            )
            
            result = {
                'video_path': final_video_path,
                'video_url': f"file://{final_video_path}",
                'title': script_data['title'],
                'duration': script_data.get('estimated_duration', 60),
                'script': script_data['script']
            }
            
            logger.info(f"Video generated successfully: {final_video_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating full video: {str(e)}")
            raise
    
    def _generate_scenes(self, scenes: List[Dict]) -> List[str]:
        """
        Generate video clips for each scene
        
        Args:
            scenes: List of scene dictionaries
            
        Returns:
            List of paths to scene video files
        """
        scene_videos = []
        
        for i, scene in enumerate(scenes):
            logger.info(f"Generating scene {i+1}/{len(scenes)}")
            
            # In production, use image/video generation APIs:
            # - Stable Diffusion
            # - DALL-E
            # - Midjourney
            # - Runway ML
            
            # For now, create placeholder scenes
            scene_path = self.output_dir / f"scene_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            
            duration = scene.get('duration', 5)
            visual_text = scene.get('visuals', f'Scene {i+1}')
            
            try:
                # Create scene with text overlay
                subprocess.run([
                    'ffmpeg',
                    '-f', 'lavfi', '-i', f'color=c=blue:s=1920x1080:d={duration}',
                    '-vf', f"drawtext=text='{visual_text[:50]}':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
                    '-c:v', 'libx264', '-t', str(duration), '-pix_fmt', 'yuv420p',
                    str(scene_path), '-y'
                ], check=True, capture_output=True)
                
                scene_videos.append(str(scene_path))
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Error creating scene {i}: {str(e)}")
        
        return scene_videos
    
    def _generate_voiceover(self, script: str) -> Optional[str]:
        """
        Generate voiceover audio from script
        
        Args:
            script: Narration script
            
        Returns:
            Path to voiceover audio file
        """
        logger.info("Generating voiceover")
        
        voiceover_path = self.output_dir / f"voiceover_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        
        try:
            # Use text-to-speech service
            # Options: OpenAI TTS, ElevenLabs, Google TTS, Azure TTS
            
            if hasattr(self.ai_client, 'audio') and self.ai_provider == 'openai':
                response = self.ai_client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=script
                )
                response.stream_to_file(str(voiceover_path))
                logger.info(f"Voiceover created: {voiceover_path}")
                return str(voiceover_path)
            else:
                # Fallback: create silent audio
                subprocess.run([
                    'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
                    '-t', '60', '-c:a', 'libmp3lame', str(voiceover_path), '-y'
                ], check=True, capture_output=True)
                return str(voiceover_path)
                
        except Exception as e:
            logger.error(f"Error generating voiceover: {str(e)}")
            return None
    
    def _combine_video_elements(self, scene_videos: List[str], 
                               voiceover: Optional[str],
                               music: Optional[str],
                               intro: Optional[str],
                               topic: str) -> str:
        """
        Combine all video elements into final video
        
        Args:
            scene_videos: List of scene video paths
            voiceover: Path to voiceover audio
            music: Path to background music
            intro: Path to intro video
            topic: Video topic for filename
            
        Returns:
            Path to final video
        """
        logger.info("Combining video elements")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        final_path = self.output_dir / f"final_{topic.replace(' ', '_')}_{timestamp}.mp4"
        
        try:
            # Create concat file for scenes
            concat_file = self.output_dir / f"concat_{timestamp}.txt"
            with open(concat_file, 'w') as f:
                if intro:
                    f.write(f"file '{intro}'\n")
                for scene in scene_videos:
                    f.write(f"file '{scene}'\n")
            
            # Concatenate videos
            temp_video = self.output_dir / f"temp_video_{timestamp}.mp4"
            subprocess.run([
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', str(concat_file),
                '-c', 'copy', str(temp_video), '-y'
            ], check=True, capture_output=True)
            
            # Add audio tracks
            audio_inputs = []
            audio_filters = []
            
            if voiceover:
                audio_inputs.extend(['-i', voiceover])
                audio_filters.append('[1:a]')
            
            if music:
                audio_inputs.extend(['-i', music])
                audio_filters.append('[2:a]volume=0.3')  # Lower music volume
            
            if audio_inputs:
                # Mix audio tracks
                filter_complex = f"{''.join(audio_filters)}amix=inputs={len(audio_filters)}:duration=first[aout]"
                
                subprocess.run([
                    'ffmpeg', '-i', str(temp_video), *audio_inputs,
                    '-filter_complex', filter_complex,
                    '-map', '0:v', '-map', '[aout]',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    str(final_path), '-y'
                ], check=True, capture_output=True)
            else:
                # No audio, just copy
                os.rename(temp_video, final_path)
            
            # Clean up temporary files
            concat_file.unlink(missing_ok=True)
            temp_video.unlink(missing_ok=True)
            
            logger.info(f"Final video created: {final_path}")
            return str(final_path)
            
        except Exception as e:
            logger.error(f"Error combining video elements: {str(e)}")
            raise
